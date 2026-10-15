---
name: calendar-planner
description: Review a chosen range (up to 14 days) of the user's past calendar, read event details, notes and attachments, then output a summary, a to-do list grouped by priority and tagged by type and project, short Slack message drafts, and suggestions. Use when the user asks for a recap, a look back at recent meetings, or a to-do list from their calendar.
---

# Calendar Planner

Look back over the user's recent calendar, find what needs follow-up, and hand back a sorted, ready-to-use to-do list in the chat.

## Step 1: Ask how far back to look

Always ask before starting, using a multiple choice question (use the AskUserQuestion tool if available, otherwise a short numbered list in chat):

- Last 3 days
- Last 7 days
- Last 10 days
- Last 14 days

The user can also type a custom number of days or a date range.

Rules:
- Maximum is 14 days. If the user asks for more, say the limit is 14 days and ask them to pick again.
- The range always ends today.
- Wait for the answer before pulling any events.

## Step 2: Pull the events

- Use the Google Calendar connector to list all events in the chosen range.
- Skip events the user declined, all-day placeholders with no content (like "Out of office" or holidays), and focus blocks with no description.
- If the calendar connector is not available, tell the user and stop.

## Step 3: Read everything attached to each event

For each event, gather:
- Title, time, attendees.
- The description and any notes in it.
- Attached or linked files (Google Docs, meeting notes, agendas, slides). Open and read them with whatever connector is available.
- If a linked file cannot be opened, note it in the output so the user knows it was skipped.

## Step 4: Find the action items

Look for anything that implies the user needs to do something, such as:
- Clear tasks ("I'll send the deck", "Alex to review").
- Promises made by the user or assigned to them.
- Open questions that were left unanswered.
- Deadlines or dates mentioned ("by Friday", "before the launch").

Only include items that belong to the user. Skip tasks clearly owned by someone else unless the user needs to chase them.

## Step 5: Categorize each task

Give every task three labels.

**Priority** (used to group the list):
- **Urgent:** due today or tomorrow, overdue, or someone is blocked waiting on the user.
- **This week:** due within the next 7 days, or clearly expected soon.
- **Later:** no date, or due more than 7 days out.

**Type:**
- **Message:** send a Slack message, reply, or quick check in.
- **Meeting:** book, move, or prepare for a meeting.
- **Write:** create or update a doc, deck, or plan.
- **Review:** read, check, or give feedback on something.
- **Decision:** make or confirm a choice.
- **Other:** anything that does not fit above.

**Project:** the project, client, or topic the task belongs to. Take it from the meeting title, notes, or attendees. If it is not clear, use "General".

## Step 6: Draft Slack messages

For every task with the type **Message**:
- Write a short, casual Slack message the user could send as is.
- Keep it to 1 to 3 sentences. Normal Slack tone. No formal greetings or sign offs.
- Address it to the right person or channel if known.
- Do not send anything. Drafts only.

## Step 7: Add suggestions

Beyond the listed tasks, offer a few of your own ideas where useful, for example:
- A meeting that ended with no clear next step and probably needs one.
- A follow-up that seems overdue.
- A person the user met with several times who may need a quick update.

Keep suggestions short and only include ones that are actually helpful.

## Output format

Reply in the chat using this layout:

**Range:** the dates covered (for example "Oct 8 to Oct 15")

**Summary**
A short paragraph or brief list of the key meetings and what came out of them.

**At a glance**
One line with counts, for example: "9 tasks: 2 Urgent, 4 This week, 3 Later. Projects: Launch (4), Hiring (3), General (2)."

**To-do list**
Group under three headings in this order: Urgent, This week, Later. Leave out any heading with no tasks.

Under each heading, list tasks sorted by due date (soonest first). For each task:
- **Task:** what needs doing
- **Type:** Message, Meeting, Write, Review, Decision, or Other
- **Project:** project or topic name
- **From:** meeting name and date
- **Due:** date if one was mentioned or implied, otherwise "No date"
- **Slack draft:** (Message tasks only) the draft message

**Suggestions**
2 to 5 short bullet points.

**Skipped**
List any files or notes that could not be opened. Leave this section out if nothing was skipped.

## Style rules

- Keep everything plain, simple, and easy to scan.
- No long explanations.
- Do not make up tasks, deadlines, or projects that are not supported by the calendar or notes. If something is unclear, mark it as unclear rather than guessing.
