############################################
# RULE 1: Remove comments from low karma / new accounts
############################################
type: comment
author:
  account_age: "< 5 days"
  combined_karma: "< 20"
action: remove
action_reason: "User has less than 20 karma and an account younger than 5 days."
comment: |
  Hi u/{{author}}, your comment has been removed because your account is less than 5 days old and/or has under 20 total karma.
  This is an anti-spam measure.

  If you believe your comment is legitimate, please send a ModMail:
  https://www.reddit.com/message/compose?to=/r/glinet

  A moderator can manually approve it. Once your account has aged and gained karma, you’ll be able to comment freely. Thanks for understanding!
message: |
  Hi {{author}},

  Your comment in r/glinet was automatically removed because your account is less than 5 days old and/or has under 20 total karma.

  If your comment was legitimate, please contact the moderators:
  https://www.reddit.com/message/compose?to=/r/glinet

  Thanks for understanding and welcome to the GL.iNet community!

---

############################################
# RULE 2: Encourage users to mark solved posts
############################################
type: submission
flair_text: ["questions/support"]
comment: |
  Hi u/{{author}}, thanks for posting your question!

  If your issue gets resolved, please help others by marking your post as Solved.

  How to do it:
  - Click the three dots "..." under your post title
  - Choose "Add Flair"
  - Select the "question/support- Solved" flair
  - Use the support template located here: https://www.reddit.com/r/GlInet/wiki/index/kb/asking_for_help

  Marking solved posts makes it easier for the community to find answers.

  Need more help? Join the GL.iNet Discord:
  https://discord.gg/Aaqf4CZMut

---

############################################
# RULE 3: Reminder to search before posting
############################################
type: submission
flair_text:
  - "news"
  - "questions/support"
  - "discussion"
  - "question/support- Solved"
comment: |
  Hi u/{{author}}, just a quick reminder:

  Please search the subreddit before posting — many common questions have already been answered.

  Search guide:
  https://www.reddit.com/r/GlInet/wiki/index/searchingwithin

  This helps keep the community organized and easier to navigate.

---

############################################
# RULE 4: Restrict "GL.iNet Affiliated Announcements" Flair
############################################

# Remove unauthorized users using restricted flair
type: submission
flair_text: ["GL.iNet Affiliated Announcements"]
author:
  name (regex, full-exact): ["^(?!wickedwarlock84$|NationalOwl9561$|RemoteToHome-io$|GLiNet_WiFi$|robotluo$|GrandWizardZippy$|Valuable-Speaker-312$).*"]
action: remove
action_reason: "Restricted flair misuse: GL.iNet Affiliated Announcements"
comment_stickied: true
comment_locked: true
comment: |
  This flair is reserved for official GL.iNet employees or affiliated accounts only.
  If this was applied in error, please contact the moderators.

---

# Auto-lock all approved Affiliated Announcement posts
type: submission
flair_text: ["GL.iNet Affiliated Announcements"]
action: lock
action_reason: "Auto-lock: Official GL.iNet Affiliated Announcement"

---

############################################
# RULE 5: Remove comments from anyone except OP on Affiliated posts
############################################
type: comment
parent_submission:
  flair_text: ["GL.iNet Affiliated Announcements"]
author:
  name (regex, full-exact): ["^(?!{{author}}$).*"]
action: remove
action_reason: "Comments restricted on official announcement posts."