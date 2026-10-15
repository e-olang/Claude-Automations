## Claude Automations

My personal collection of Claude automations: Claude skills, plus small apps that call Claude, mostly for meetings and planning work around my Google Calendar, Google Drive and Slack.

## What's here

| Folder | Automation | Type | What it does |
|---|---|---|---|
| `Meeting Ai 2.0/claude_skills/meeting-prep` | meeting-prep | Claude skill | Preps talking points for my next meeting by looking back over the last 1–4 weeks of work |
| `Meeting Ai 2.0/Meeting Assistant/claude` | meeting-assistant | Claude skill | Summarises Google Meet meetings from their Gemini notes, posts them to Slack, and drafts agendas |
| `Meeting Ai 2.0/Meeting Assistant/python_app` | Meeting Assistant | Python app | Script version of meeting-assistant that summarises recent meetings and posts agendas to Slack |
| `Task Planner/calendar-planner` | calendar-planner | Claude skill | Reviews up to 14 days of past calendar and returns a summary, a prioritised to-do list with Slack drafts, a Google Keep checklist and suggestions |

## Using the skills

Each skill is a folder with a `SKILL.md` and a matching `.zip`. To install one, upload the `.zip` in Claude under **Settings → Capabilities → Skills**, or copy the folder into `~/.claude/skills/` for Claude Code.

Most skills expect the Google Calendar, Google Drive and Slack connectors to be connected.

## Running the Python app

Setup and usage are in [the app's README](Meeting%20Ai%202.0/Meeting%20Assistant/python_app/README.md). Secrets go in a `.env` file in that folder, which git ignores.

## Adding a new automation

1. Make a folder for the project at the top level.
2. For a skill, keep the `SKILL.md` source next to its `.zip`.
3. For an app, include its own README and `.gitignore`, and keep secrets out of git.
4. Add a row to the table above.
