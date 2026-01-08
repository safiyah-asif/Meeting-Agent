# my_agents/meeting_rescheduler.py

from agents import Agent, function_tool
from calendar_setup import update_event, list_meetings_for_selection, get_credentials
from email_utils import send_email
from googleapiclient.discovery import build
from calendar_tools import check_slot_free, resolve_meeting_by_index
from meeting_selector import show_meeting_selection
from dateutil import parser
import datetime


PKT = datetime.timezone(datetime.timedelta(hours=5))


@function_tool
def reschedule_meeting(selection_number: int | None = None,
                       new_date: str | None = None,
                       new_time: str | None = None):
    """
    Reschedule an existing meeting:
    1. Fetch upcoming meetings
    2. Display list if no selection_number is provided
    3. Parse new date/time
    4. Check for conflicts
    5. Update the meeting in Google Calendar
    """
    # Step 1: Fetch upcoming meetings
    meetings = list_meetings_for_selection()
    if not meetings:
        return {"status": "Failed", "message": "No upcoming meetings found."}

    # Step 2: If selection_number not provided, reuse shared selector
    if selection_number is None:
        return show_meeting_selection()

    # Step 3: Resolve event_id and get old event info
    event_id = resolve_meeting_by_index(int(selection_number))
    if not event_id:
        return {"status": "Failed", "message": "Invalid meeting selection."}

    old_event = meetings[int(selection_number) - 1]
    title = old_event.get("label", "No Title")
    description = old_event.get("description", "")

    # Step 4: Parse new date/time
    # try:
    #     new_start = parser.parse(f"{new_date} {new_time}").replace(tzinfo=PKT)
    # except Exception as e:
    #     return {"status": "Failed", "message": f"Invalid date/time format: {e}"}

    # new_end = new_start + datetime.timedelta(hours=1)
    # Step 4: Parse new date/time
    try:
        new_start = parser.parse(f"{new_date} {new_time}").replace(tzinfo=PKT)
    except Exception as e:
        return {"status": "Failed", "message": f"Invalid date/time format: {e}"}

    # 🔧 Validate new date is not in the past
    today = datetime.datetime.now(PKT).replace(
        hour=0, minute=0, second=0, microsecond=0)
    new_start_date = new_start.replace(
        hour=0, minute=0, second=0, microsecond=0)
    if new_start_date < today:
        return {
            "status": "Failed",
            "message": f"❌ Cannot reschedule meeting to {new_date}. The date is in the past. Please provide a future date (today or later)."
        }

    new_end = new_start + datetime.timedelta(hours=1)
    # Step 5: Check for conflicts
    if not check_slot_free(new_start, new_end, exclude_event_id=event_id):
        return {"status": "Failed", "message": "Time slot clashes with another meeting."}

    # Step 6: Update the meeting in place
    result = update_event(event_id, new_start, new_end)
    if result.get("status") != "Success":
        return {"status": "Failed", "message": "Failed to update the meeting."}

    # Fetch updated event details to notify attendees
    email_results = []
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)
        event_obj = service.events().get(calendarId="primary", eventId=event_id).execute()
        attendees = event_obj.get("attendees", [])
        html_link = event_obj.get("htmlLink")
        # Fallback: if attendees empty, try to parse emails from description
        if not attendees:
            import re
            desc = event_obj.get("description", "") or ""
            emails = re.findall(r"[\w\.-]+@[\w\.-]+", desc)
            attendees = [{"email": e} for e in sorted(set(emails))]
    except Exception:
        attendees = []
        html_link = result.get("htmlLink")

    email_subject = f"Meeting Rescheduled: {title}"
    for a in attendees:
        to_email = a.get("email")
        if not to_email:
            continue
        body = (
            f"Hello,\n\n"
            f"The meeting '{title}' has been rescheduled to {new_start.strftime('%b %d, %Y, %H:%M')} PKT.\n"
            f"Link: {html_link}\n\n"
            f"Regards,\nMeeting Bot"
        )
        try:
            res = send_email(to_email, email_subject, body)
        except Exception as e:
            res = {"status": "Failed", "message": str(e)}
        email_results.append({"email": to_email, "result": res})

    return {
        "status": "Rescheduled",
        "message": f"✅ Meeting '{title}' has been rescheduled to {new_start.strftime('%b %d, %Y, %H:%M')} PKT.",
        "calendar_link": html_link,
        "email_results": email_results,
    }


def meeting_rescheduler_agent(model):
    return Agent(
        name="Meeting Rescheduler",
        instructions="""
        You are a meeting rescheduling assistant.
        - Always fetch upcoming meetings from Google Calendar using list_meetings_for_selection().
        - Display the list to the user with numbers, e.g.:
            1) Project Discussion — Dec 25, 11:00
            2) Teach for Pakistan — Dec 26, 14:00
        - Ask the user to select which meeting to reschedule by its number.
        - Then ask for the new date (YYYY-MM-DD) and new time (HH:MM or HH:MM AM/PM).
        - Do not ask the user for meeting IDs.
        - Confirm rescheduling and update the actual Google Calendar event using update_event().
        - Accept 12h or 24h time format.
        - **Validate dates:** Only accept future dates for rescheduling. Reject any past dates immediately.
        - If the user tries to reschedule to a past date, ask them to provide a future date instead.
        - Format required: YYYY-MM-DD (e.g., 2026-01-15)
        - Handle errors gracefully and inform the user.
        """,
        tools=[reschedule_meeting],
        model=model
    )
