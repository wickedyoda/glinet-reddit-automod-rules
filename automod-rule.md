# Rule 1: Remove comments from users with low karma and new accounts
type: comment
author:
  account_age: "< 5 days"
  combined_karma: "< 20"

action: remove
action_reason: "User has less than 20 karma and an account younger than 5 days. Please use ModMail to speak to a mod and have your post approved manually."

comment: |
  Hi u/{{author}}, your comment has been removed because your account is less than 5 days old and/or has under 20 total karma.
  This is an anti-spam measure.

  If you believe your comment is legitimate, please send a ModMail:
  https://www.reddit.com/message/compose?to=/r/glinet

  A moderator can manually approve it. Once your account has aged and gained karma, you’ll be able to comment freely. Thanks for understanding!

message: |
  Hi {{author}},

  Your comment in r/glinet was automatically removed because your account is less than 5 days old and/or has under 20 total karma. This rule helps us reduce spam and keep discussions productive.

  If your comment was legitimate, you’re welcome to contact the moderators via ModMail:
  https://www.reddit.com/message/compose?to=/r/glinet

  A moderator can manually review and approve it. Once your account gains a bit more age and karma, you’ll be able to participate normally.

  Thanks for understanding and welcome to the GL.iNet community!

# Rule 2: Encourage users to mark solved posts (only when flair is "questions/support")
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

  Need more help? Join the GL.iNet Discord for advanced support and real-time community help:
  https://discord.gg/Aaqf4CZMut

# Rule 3: Generic reminder to search before posting (all posts except "GL.iNet Announcements")
type: submission
flair_text:
  - "news"
  - "questions/support"
  - "discussion"
  - "question/support- Solved"
comment: |
  Hi u/{{author}}, just a quick reminder:
  Please search the subreddit before posting — many common questions have already been answered.

  Need help searching? Check out our guide:
  https://www.reddit.com/r/GlInet/wiki/index/searchingwithin

  This helps keep the community clean and makes it easier for everyone to find answers.
