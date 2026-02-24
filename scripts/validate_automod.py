#!/usr/bin/env python3
"""Validate AutoModerator YAML using the local Reddit spec document."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from yaml.loader import SafeLoader


class UniqueKeyLoader(SafeLoader):
    """YAML loader that fails on duplicate keys."""



def _construct_mapping(loader: UniqueKeyLoader, node: yaml.Node, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            line = key_node.start_mark.line + 1
            raise yaml.YAMLError(f"duplicate key `{key}` at line {line}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(  # type: ignore[arg-type]
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


TYPE_VALUES_RE = re.compile(r"type - .*?Valid values are ([^.]+)\.", re.IGNORECASE | re.DOTALL)
SUBMISSION_ACTION_VALUES_RE = re.compile(
    r"For submissions \(base item or parent_submission sub-group\):.*?"
    r"action - .*?Valid values are ([^.]+)\.",
    re.IGNORECASE | re.DOTALL,
)
COMMENT_ACTION_VALUES_RE = re.compile(
    r"For comments \(base item only\):.*?action - .*?Valid values are ([^\.\n]+)",
    re.IGNORECASE | re.DOTALL,
)
BOOL_KEY_RE = re.compile(r"^([a-z_]+)\s*-\s*true/false\b", re.IGNORECASE | re.MULTILINE)
NUMERIC_KEY_RE = re.compile(
    r"^([a-z_]+)\s*-\s*must be set to a number\b",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class AutomodSpec:
    allowed_types: set[str]
    submission_actions: set[str]
    comment_actions: set[str]
    boolean_keys: set[str]
    numeric_keys: set[str]


def _parse_natural_list(raw_values: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", "", raw_values)
    cleaned = cleaned.replace(" or ", ", ").replace(" and ", ", ")
    items = [item.strip().strip("'\"`.").lower() for item in cleaned.split(",")]
    return {item for item in items if item}


def _extract_required_values(text: str, regex: re.Pattern[str], label: str) -> set[str]:
    match = regex.search(text)
    if not match:
        raise ValueError(f"Unable to extract {label} from reddit_automod_rules.md")
    return _parse_natural_list(match.group(1))


def load_spec(path: Path) -> AutomodSpec:
    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {path}")

    text = path.read_text(encoding="utf-8")

    allowed_types = _extract_required_values(text, TYPE_VALUES_RE, "allowed types")
    submission_actions = _extract_required_values(
        text,
        SUBMISSION_ACTION_VALUES_RE,
        "submission actions",
    )
    comment_actions = _extract_required_values(
        text,
        COMMENT_ACTION_VALUES_RE,
        "comment actions",
    )

    boolean_keys = {match.group(1).lower() for match in BOOL_KEY_RE.finditer(text)}
    numeric_keys = {match.group(1).lower() for match in NUMERIC_KEY_RE.finditer(text)}

    return AutomodSpec(
        allowed_types=allowed_types,
        submission_actions=submission_actions,
        comment_actions=comment_actions,
        boolean_keys=boolean_keys,
        numeric_keys=numeric_keys,
    )


def _validate_key_value_types(value: Any, spec: AutomodSpec, rule_name: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                key_name = key.lower()
                if key_name in spec.boolean_keys and not isinstance(child, bool):
                    errors.append(f"{rule_name}: `{key}` must be true/false.")
                if key_name in spec.numeric_keys and (
                    not isinstance(child, (int, float)) or isinstance(child, bool)
                ):
                    errors.append(f"{rule_name}: `{key}` must be numeric.")
            _validate_key_value_types(child, spec, rule_name, errors)
        return

    if isinstance(value, list):
        for item in value:
            _validate_key_value_types(item, spec, rule_name, errors)


def _allowed_actions_for_type(rule_type: str, spec: AutomodSpec) -> set[str]:
    if rule_type == "comment":
        return spec.comment_actions
    if rule_type == "any":
        return spec.comment_actions | spec.submission_actions
    return spec.submission_actions


def validate(target_path: Path, spec_path: Path) -> list[str]:
    errors: list[str] = []

    try:
        spec = load_spec(spec_path)
    except (FileNotFoundError, ValueError) as exc:
        return [str(exc)]

    if not target_path.exists():
        return [f"File not found: {target_path}"]

    raw_text = target_path.read_text(encoding="utf-8")

    try:
        docs = list(yaml.load_all(raw_text, Loader=UniqueKeyLoader))
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"]

    if not docs:
        return ["No rules found: expected one or more YAML documents."]

    separator_count = len(re.findall(r"(?m)^---\s*$", raw_text))
    type_line_count = len(re.findall(r"(?m)^type\s*:", raw_text))
    if type_line_count > len(docs):
        errors.append(
            "Potential missing YAML document separators (`---`): found more top-level "
            "`type:` keys than parsed YAML documents."
        )
    if len(docs) > 1 and separator_count < len(docs) - 1:
        errors.append("Rules must be separated with lines containing exactly `---`.")

    for index, doc in enumerate(docs, start=1):
        rule_name = f"Rule {index}"

        if doc is None:
            errors.append(f"{rule_name}: empty YAML document.")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{rule_name}: top-level document must be a mapping/object.")
            continue

        raw_type = doc.get("type", "any")
        if not isinstance(raw_type, str):
            errors.append(f"{rule_name}: `type` must be a string when provided.")
            rule_type = "any"
        else:
            rule_type = raw_type.strip().lower()
            if rule_type not in spec.allowed_types:
                errors.append(
                    f"{rule_name}: invalid `type` value `{raw_type}`. "
                    f"Allowed: {', '.join(sorted(spec.allowed_types))}."
                )

        if "parent_submission" in doc and rule_type != "comment":
            errors.append(f"{rule_name}: `parent_submission` can only be used when `type: comment`.")

        action = doc.get("action")
        if action is not None:
            if not isinstance(action, str):
                errors.append(f"{rule_name}: `action` must be a string when provided.")
            else:
                normalized_action = action.strip().lower()
                allowed_actions = _allowed_actions_for_type(rule_type, spec)
                if normalized_action not in allowed_actions:
                    errors.append(
                        f"{rule_name}: invalid `action` value `{action}` for type `{rule_type}`. "
                        f"Allowed: {', '.join(sorted(allowed_actions))}."
                    )

        _validate_key_value_types(doc, spec, rule_name, errors)

    return errors


def _default_target_path() -> str:
    for candidate in ("automod-main-rule.md", "automod-rule.md"):
        if Path(candidate).exists():
            return candidate
    return "automod-main-rule.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        nargs="?",
        default=_default_target_path(),
        help="Path to the AutoModerator rules file to validate.",
    )
    parser.add_argument(
        "--spec",
        default="reddit_automod_rules.md",
        help="Path to the spec text file used to derive validation constraints.",
    )
    args = parser.parse_args()

    target = Path(args.target)
    spec_path = Path(args.spec)

    issues = validate(target, spec_path)
    if issues:
        print("AutoModerator validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(
        "AutoModerator validation passed for "
        f"{target} using spec {spec_path}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
