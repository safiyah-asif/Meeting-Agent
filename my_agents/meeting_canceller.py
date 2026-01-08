from agents import Agent, function_tool
from calendar_tools import resolve_meeting_by_index
from calendar_setup import delete_event, list_meetings_for_selection, PKT, get_credentials
from email_utils import send_email
from googleapiclient.discovery import build
from meeting_selector import show_meeting_selection
from datetime import datetime


@function_tool
def show_upcoming_meetings():
    """
    Returns upcoming meetings for the user to select from.
    Uses list_meetings_for_selection() from calendar_setup.py
    and formats the start time in PKT.
    """
    meetings = list_meetings_for_selection()
    if not meetings:
        return {"status": "Failed", "message": "No upcoming meetings found."}

    display_list = []
    for m in meetings:
        # Convert ISO start time to PKT datetime for display
        try:
            start_dt = datetime.fromisoformat(
                m['label'].split(" — ")[1]).astimezone(PKT)
            display_label = f"{m['index']}. {m['label'].split(' — ')[0]} — {start_dt.strftime('%Y-%m-%d %H:%M %Z')}"
        except Exception:
            # Fallback if parsing fails
            display_label = f"{m['index']}. {m['label']}"
        display_list.append(display_label)

    return {"status": "Success", "meetings": meetings, "display": "\n".join(display_list)}


@function_tool
def cancel_meeting(selection_number: int | None = None, reason: str | None = None):
    """
    Cancels a meeting from Google Calendar.
    Allows user to select a meeting by number from show_meeting_selection().
    """
    # Step 1: If no selection, show meeting list
    if selection_number is None:
        return show_meeting_selection()

    # Step 2: Resolve index → actual event_id
    event_id = resolve_meeting_by_index(selection_number)
    if not event_id:
        return {"status": "Failed", "message": "Invalid meeting selection."}

    # Step 3: Get meeting label for confirmation
    meeting_label = None
    meetings = list_meetings_for_selection()
    for m in meetings:
        if m["event_id"] == event_id:
            meeting_label = m.get("label")
            break

    # Step 4: Cancel the meeting
    # Fetch attendees before deletion so we can notify them
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)
        event_obj = service.events().get(calendarId="primary", eventId=event_id).execute()
        attendees = event_obj.get("attendees", [])
        # Fallback: parse emails from description if attendees missing
        if not attendees:
            import re
            desc = event_obj.get("description", "") or ""
            emails = re.findall(r"[\w\.-]+@[\w\.-]+", desc)
            attendees = [{"email": e} for e in sorted(set(emails))]
    except Exception:
        attendees = []

    result = delete_event(event_id)
    if result["status"] == "Failed":
        return {"status": "Failed", "event_id": event_id, "message": result["message"]}

    # Notify attendees about cancellation
    email_subject = f"Meeting Cancelled: {meeting_label or event_id}"
    email_results = []
    for a in attendees:
        to_email = a.get("email")
        if not to_email:
            continue
        body = (
            f"Hello,\n\n"
            f"The meeting '{meeting_label or event_id}' has been cancelled.\n"
            f"Reason: {reason or 'Not specified'}\n\n"
            f"If you have questions, contact the organizer.\n\n"
            f"Regards,\nMeeting Bot"
        )
        try:
            res = send_email(to_email, email_subject, body)
        except Exception as e:
            res = {"status": "Failed", "message": str(e)}
        email_results.append({"email": to_email, "result": res})

    return {
        "meeting_id": event_id,
        "status": "Cancelled",
        "reason": reason or "Not specified",
        "message": f"✅ Meeting '{meeting_label or event_id}' cancelled successfully.",
        "email_results": email_results,
    }


def meeting_canceller_agent(model):
    return Agent(
        name="Meeting Canceller",
        instructions="""
        You are a Google Calendar assistant.
        - Use show_meeting_selection() to list upcoming meetings for the user.
        - Use cancel_meeting(event_id, reason) to cancel a meeting.
          The event_id can be the actual ID or the index from show_meeting_selection().
        - Ask the user to select a meeting by number.  
        - Ask politely which meeting the user wants to cancel if not provided.
        - Ask for a cancellation reason if not provided.
        - Proceed even if the user does not give a reason.
        - Never block cancellation due to missing reason.
        - Confirm cancellation clearly.
        """,
        tools=[show_upcoming_meetings, cancel_meeting],
        model=model
    )
