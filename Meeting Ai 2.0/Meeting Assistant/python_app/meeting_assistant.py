"""
Meeting assistant — one simple script.

    python meeting_assistant.py summarize    # summarise meetings that ended in the last 24 hours
    python meeting_assistant.py agenda       # draft agendas for tomorrow's meetings

Add --dry-run to print the Slack messages instead of posting them.
"""

import json
import os
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import anthropic
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from slack_sdk import WebClient

# ---------------------------------------------------------------------------
# Settings — change these if you like
# ---------------------------------------------------------------------------

TIMEZONE = ZoneInfo("Africa/Nairobi")
CLAUDE_MODEL = "claude-haiku-5-5"
LOOKBACK_HOURS = 24        # summarize: meetings that ended in the last 24 hours
HISTORY_DAYS = 90          # agenda: how far back to look for earlier meetings
MAX_EARLIER_MEETINGS = 3   # agenda: how many earlier meetings to use

FOLDER = Path(__file__).parent  # this script's folder — all files below live here
POSTED_FILE = FOLDER / "posted.json"  # remembers what we already posted
TOKEN_FILE = FOLDER / "token.json"    # your saved Google sign-in
CLIENT_SECRET_FILE = FOLDER / "client_secret.json"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

SUMMARY_INSTRUCTIONS = """You summarise meeting notes for a Slack channel.
Use Slack formatting: *bold* for headings and • for bullets.
Write these sections: Key points, Decisions, Action items (with the owner of each).
Keep it short. Only use what is in the notes — never make things up."""

AGENDA_INSTRUCTIONS = """You draft an agenda for an upcoming meeting, using notes from earlier meetings.
Use Slack formatting: *bold* for headings and • for bullets.
Write these sections: Goal (one line), Open action items (with owners), Topics (3-6, with suggested minutes).
Only use what is in the notes — never make things up."""

load_dotenv(FOLDER / ".env")  # reads your secrets from the .env file


# ---------------------------------------------------------------------------
# Google: calendar and notes
# ---------------------------------------------------------------------------

def google_login():
    """Sign in to Google. The first time, a browser opens; after that token.json is reused."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, GOOGLE_SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, GOOGLE_SCOPES)
        creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json())
    calendar = build("calendar", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return calendar, drive


def get_meetings(calendar, start, end):
    """Google Meet meetings on my calendar between start and end."""
    result = calendar.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=250,
    ).execute()
    return [event for event in result.get("items", []) if is_meet_meeting(event)]


def is_meet_meeting(event):
    """True if the event has a Google Meet link, a start time, and I haven't declined it."""
    if not event.get("hangoutLink") or "dateTime" not in event.get("start", {}):
        return False
    for person in event.get("attendees", []):
        if person.get("self") and person.get("responseStatus") == "declined":
            return False
    return True


def find_notes_doc(event):
    """The attached 'Notes by Gemini' doc, or the transcript if there are no notes, or None."""
    docs = [a for a in event.get("attachments", [])
            if a.get("mimeType") == "application/vnd.google-apps.document"]
    for doc in docs:
        if "notes by gemini" in doc.get("title", "").lower():
            return doc
    for doc in docs:
        if "transcript" in doc.get("title", "").lower():
            return doc
    return None


def read_doc(drive, file_id):
    """Download a Google Doc as plain text."""
    return drive.files().export(fileId=file_id, mimeType="text/plain").execute().decode("utf-8")


def end_time(event):
    return datetime.fromisoformat(event["end"]["dateTime"])


# ---------------------------------------------------------------------------
# Claude and Slack
# ---------------------------------------------------------------------------

def ask_claude(instructions, text):
    """Send text to Claude and return its reply. Uses ANTHROPIC_API_KEY from .env."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=16000,
        system=instructions,
        messages=[{"role": "user", "content": text}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def post_to_slack(message, dry_run):
    """Post a message to the Slack channel in .env (or just print it in dry-run mode)."""
    if dry_run:
        print("\n----- DRY RUN: would post to Slack -----\n" + message + "\n")
        return
    slack = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    slack.chat_postMessage(channel=os.environ["SLACK_CHANNEL_ID"], text=message)


# ---------------------------------------------------------------------------
# Remembering what we already posted
# ---------------------------------------------------------------------------

def load_posted():
    if POSTED_FILE.exists():
        return json.loads(POSTED_FILE.read_text())
    return {"summaries": [], "agendas": []}


def save_posted(posted):
    POSTED_FILE.write_text(json.dumps(posted, indent=2))


# ---------------------------------------------------------------------------
# The two jobs
# ---------------------------------------------------------------------------

def summarize(dry_run):
    calendar, drive = google_login()
    posted = load_posted()
    now = datetime.now(TIMEZONE)

    for event in get_meetings(calendar, now - timedelta(hours=LOOKBACK_HOURS), now):
        title = event.get("summary", "Untitled meeting")

        if event["id"] in posted["summaries"]:
            continue  # already posted
        if end_time(event) > now:
            continue  # still going

        doc = find_notes_doc(event)
        if doc is None:
            print(f"No notes yet for '{title}' — will check again next time.")
            continue

        print(f"Summarising '{title}'...")
        notes = read_doc(drive, doc["fileId"])
        summary = ask_claude(SUMMARY_INSTRUCTIONS, f"Meeting: {title}\n\nNotes:\n{notes}")
        post_to_slack(f"*📝 Summary: {title}*\n<{doc['fileUrl']}|Open the notes>\n\n{summary}", dry_run)

        if not dry_run:
            posted["summaries"].append(event["id"])
            save_posted(posted)


def agenda(dry_run):
    calendar, drive = google_login()
    posted = load_posted()
    now = datetime.now(TIMEZONE)
    tomorrow = datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=TIMEZONE)

    for event in get_meetings(calendar, tomorrow, tomorrow + timedelta(days=1)):
        title = event.get("summary", "Untitled meeting")
        if event["id"] in posted["agendas"]:
            continue  # already posted

        # Collect notes from earlier meetings in the same series (or with the same title)
        earlier_notes = []
        for old in get_earlier_meetings(calendar, event, now):
            doc = find_notes_doc(old)
            if doc:
                date = old["start"]["dateTime"][:10]
                earlier_notes.append(f"--- Notes from {date} ---\n{read_doc(drive, doc['fileId'])}")

        if not earlier_notes:
            print(f"No earlier notes for '{title}' — skipping agenda.")
            continue

        print(f"Drafting agenda for '{title}'...")
        text = f"Upcoming meeting: {title}\n\n" + "\n\n".join(earlier_notes)
        agenda_text = ask_claude(AGENDA_INSTRUCTIONS, text)
        post_to_slack(f"*🗓️ Agenda for tomorrow: {title}*\n\n{agenda_text}", dry_run)

        if not dry_run:
            posted["agendas"].append(event["id"])
            save_posted(posted)


def get_earlier_meetings(calendar, event, now):
    """Past meetings from the same recurring series, or with the same title. Newest last."""
    series = event.get("recurringEventId")
    title = event.get("summary", "").lower()
    past = get_meetings(calendar, now - timedelta(days=HISTORY_DAYS), now)
    related = [
        old for old in past
        if (series and old.get("recurringEventId") == series) or old.get("summary", "").lower() == title
    ]
    return related[-MAX_EARLIER_MEETINGS:]


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    dry_run = "--dry-run" in sys.argv

    if command == "summarize":
        summarize(dry_run)
    elif command == "agenda":
        agenda(dry_run)
    else:
        print(__doc__)
