from agents import Agent, function_tool
from calendar_setup import list_meetings_for_selection, get_credentials
from calendar_tools import resolve_meeting_by_index
from meeting_selector import show_meeting_selection
from googleapiclient.discovery import build
from email_utils import send_email


@function_tool
def update_meeting(selection_number: int | None = None,
                   new_title: str | None = None,
                   add_attendees: list[str] | None = None,
                   remove_attendees: list[str] | None = None):
    """
    Update a meeting's title or participants.
    Returns the updated meeting details.
    """
    # List meetings if selection_number not provided
    if selection_number is None:
        return show_meeting_selection()

    # Resolve event_id
    event_id = resolve_meeting_by_index(int(selection_number))
    if not event_id:
        return {"status": "Failed", "message": "Invalid meeting selection."}

    # Ensure at least one update is provided
    if not new_title and not add_attendees and not remove_attendees:
        return {"status": "Failed", "message": "No updates provided. Please provide a new title or participants to add/remove."}

    # Access Google Calendar
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    event = service.events().get(calendarId="primary", eventId=event_id).execute()

    # Prepare update body
    update_body = {
        "start": event["start"],  # preserve start time
        "end": event["end"],      # preserve end time
        "summary": new_title if new_title else event.get("summary", "")
    }

    # Preserve existing attendees
    attendees = event.get("attendees", [])

    # Remove attendees if requested
    if remove_attendees:
        attendees = [a for a in attendees if a["email"]
                     not in remove_attendees]

    # Add new attendees if requested
    if add_attendees:
        existing_emails = {a["email"] for a in attendees}
        for email in add_attendees:
            if email not in existing_emails:
                attendees.append({"email": email})

    # Always include attendees field to preserve existing participants
    update_body["attendees"] = attendees

    # Execute the update
    updated_event = service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=update_body
    ).execute()

    # Prepare updated details
    updated_details = {
        "Title": updated_event.get("summary", ""),
        "Organizer": updated_event.get("organizer", {}).get("email", ""),
        "Participants": [a["email"] for a in updated_event.get("attendees", [])] if updated_event.get("attendees") else [],
        "Start": updated_event["start"].get("dateTime", updated_event["start"].get("date")),
        "End": updated_event["end"].get("dateTime", updated_event["end"].get("date")),
        "Calendar Link": updated_event.get("htmlLink")
    }

    # Notify attendees about update
    attendees = updated_event.get("attendees", []) or []
    # Fallback: parse emails from description if attendees missing
    if not attendees:
        import re
        desc = updated_event.get("description", "") or ""
        emails = re.findall(r"[\w\.-]+@[\w\.-]+", desc)
        attendees = [{"email": e} for e in sorted(set(emails))]
    email_results = []
    email_subject = f"Meeting Updated: {updated_details['Title']}"
    for a in attendees:
        to_email = a.get("email")
        if not to_email:
            continue
        body = (
            f"Hello,\n\n"
            f"The meeting '{updated_details['Title']}' has been updated.\n\n"
            f"Updated details:\n"
            f"Title: {updated_details['Title']}\n"
            f"Start: {updated_details['Start']}\n"
            f"End: {updated_details['End']}\n"
            f"Link: {updated_details['Calendar Link']}\n\n"
            f"Regards,\nMeeting Bot"
        )
        try:
            res = send_email(to_email, email_subject, body)
        except Exception as e:
            res = {"status": "Failed", "message": str(e)}
        email_results.append({"email": to_email, "result": res})

    return {
        "status": "Updated",
        "message": "✅ Meeting has been updated successfully.",
        "details": updated_details,
        "email_results": email_results,
    }


def meeting_update_agent(model):
    return Agent(
        name="Meeting Updater",
        instructions="""
        You are a meeting update assistant.
        - Fetch upcoming meetings from Google Calendar and list them.
        - Ask the user to select which meeting to update.
        - Allow updates only for title or adding/removing participants.
        - Only update fields the user provides.
        - Preserve start/end times unless the user wants to change them.
        - Return full updated meeting details including organizer, participants, start/end times, and calendar link.
        """,
        tools=[update_meeting],
        model=model
    )
