# glinet-reddit-automod-rules

AutoModerator rules and validation tooling for r/glinet.

## Repository layout

- `automod_scripts/automod-main-rule.yaml`: Primary AutoModerator rule file.
- `automod_scripts/reddit_automod_rules.md`: Local Reddit AutoModerator spec reference.
- `scripts/validate_automod.py`: Validator used locally and in CI.
- `.github/workflows/automod-status-check.yml`: GitHub Actions validation workflow.

## Local validation

Run from repo root:

```bash
python3 scripts/validate_automod.py
```

Explicit file paths:

```bash
python3 scripts/validate_automod.py automod_scripts/automod-main-rule.yaml --spec automod_scripts/reddit_automod_rules.md
```

The validator checks YAML parsing, duplicate keys, rule/action/type constraints, value types, separator usage, and invalid decorative hash separators.

## Rule formatting requirements

- Use one title comment line per rule, for example: `# RULE 1: ...`
- Separate rules with lines containing exactly `---`
- Do not use decorative hash separator lines like `##########` above or below rule titles

## GitHub Actions validation

The `AutoMod Status Check` workflow runs:

- On every pull request update (`opened`, `synchronize`, `reopened`, `ready_for_review`)
- On every push to `main` (including merge commits)
