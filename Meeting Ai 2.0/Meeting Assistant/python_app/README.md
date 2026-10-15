# Meeting Assistant

A single Python script that:

- **`summarize`**: finds Google Meet meetings that ended in the last 24 hours, reads their Gemini notes
  (or the transcript), asks Claude for a summary, and posts it to Slack.
- **`agenda`**: finds tomorrow's meetings, reads the notes from earlier meetings in the same series, asks
  Claude for an agenda, and posts it to Slack.

It remembers what it has already posted in `posted.json`, so nothing gets posted twice.

## Files

| File | What it is |
|---|---|
| `meeting_assistant.py` | The whole program |
| `test_meeting_assistant.py` | One small test |
| `requirements.txt` | Python packages to install |
| `.env` | Your secrets (never shared — git ignores it) |

## 1. Set up Python

With venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or with conda:

```bash
conda create -n meetings python=3.12
conda activate meetings
pip install -r requirements.txt
```

Check that it works:

```bash
pytest
```

## 2. Google (one time, about 10 min)

1. Go to <https://console.cloud.google.com/> with your work account and create a project.
2. **APIs & Services → Library**: enable **Google Calendar API** and **Google Drive API**.
3. **OAuth consent screen**: choose **Internal**, and give it a name and your email.
4. **Credentials → Create credentials → OAuth client ID → Desktop app**. Download the JSON file, rename it
   to `client_secret.json`, and put it in this folder.

The first time you run the script, a browser opens so you can sign in. After that it reuses
`token.json`. Access is read-only.

## 3. Slack (one time, about 5 min)

1. Go to <https://api.slack.com/apps>, click **Create New App → From scratch**, and pick your workspace.
2. **OAuth & Permissions → Bot Token Scopes**: add `chat:write`.
3. Click **Install to Workspace**, then copy the **Bot User OAuth Token** (it starts with `xoxb-`).
4. In your Slack channel, type `/invite @YourAppName`.
5. Get the channel ID: click the channel name, and you'll find it at the bottom of the About tab.

## 4. Add your secrets

Put your secrets in a file called `.env` in this folder:

```
ANTHROPIC_API_KEY=sk-ant-...      # from https://console.anthropic.com/settings/keys
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C0123ABCDEF
```

## 5. Run it

Try it safely first. `--dry-run` prints the messages instead of posting them:

```bash
python meeting_assistant.py summarize --dry-run
python meeting_assistant.py agenda --dry-run
```

When it looks right, run it for real:

```bash
python meeting_assistant.py summarize
python meeting_assistant.py agenda
```

To post something again, delete `posted.json`.

## Later (not built yet, on purpose)

- Running automatically on a schedule in the cloud
- Posting to a DM or a Slack Canvas instead of a channel
- @mentioning action-item owners, and tracking action items across meetings
- A "no notes found" notice
- Smarter matching of related meetings (it uses the same series, or exactly the same title, for now)
- Skipping weekends (on Fridays, "tomorrow" means Saturday for now)
