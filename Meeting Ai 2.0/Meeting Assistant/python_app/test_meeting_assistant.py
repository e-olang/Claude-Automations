"""Run with:  pytest"""

from meeting_assistant import find_notes_doc

DOC = "application/vnd.google-apps.document"


def test_find_notes_doc():
    notes = {"title": "Weekly Sync - Notes by Gemini", "mimeType": DOC}
    transcript = {"title": "Weekly Sync - Transcript", "mimeType": DOC}
    video = {"title": "Weekly Sync - Recording", "mimeType": "video/mp4"}

    # Gemini notes win over the transcript
    assert find_notes_doc({"attachments": [transcript, notes]}) == notes
    # No notes? Use the transcript
    assert find_notes_doc({"attachments": [video, transcript]}) == transcript
    # Nothing useful attached
    assert find_notes_doc({"attachments": [video]}) is None
    assert find_notes_doc({}) is None
