from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
# Imports the class that holds and refreshes your Google login tokens, letting your app securely access APIs like Google Calendar
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

PKT = datetime.timezone(datetime.timedelta(hours=5))

# It gives us the access to read/write to the users calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Get valid credentials for google calendar API


def get_credentials():
    creds = None
    # Load existing credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no credentials or invalid, refresh or login
    if not creds or not creds.valid:
        if creds and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "D:/Eishal Work/6th Semester/Meeting-Agent/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save new credentials
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

# Create an event in Google Calendar


def create_event(title, description, start_datetime, end_datetime, location=None, attendees=None, send_updates: bool = False):
    """
    Adds a meeting to Google Calendar.
    start_datetime and end_datetime should be in datetime objects.
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": title,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Karachi",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Karachi",
        },

    }

    if attendees:
        event["attendees"] = []
        for a in attendees:
            entry = {"email": a.get("email")}
            if a.get("name"):
                entry["displayName"] = a.get("name")
            event["attendees"].append(entry)

    # Try inserting the event and catch errors
    try:
        created_event = service.events().insert(
            calendarId="primary", body=event).execute()
    except Exception as e:
        print("Error creating event:", e)
        return {"status": "Failed", "message": str(e)}

    return {
        "event_id": created_event.get("id"),
        "htmlLink": created_event.get("htmlLink"),
        "status": "Created"

    }

# for meeting selection (cancel_agent, reschedule_agent)
def list_meetings_for_selection(max_results=10):
    """
    Returns a numbered list of upcoming meetings with actual Google Calendar event_ids.
    """
    events = list_upcoming_events(max_results=max_results)
    selectable = []
    for idx, e in enumerate(events, start=1):
        selectable.append({
            "index": idx,
            "label": f"{e['summary']} — {e['start']}",
            "event_id": e["event_id"]  # ⚡ real Google event ID
        })
    return selectable


# List upcoming events

def list_upcoming_events(max_results=10):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    events_result = service.events().list(
        calendarId="primary",
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    return [{
        "event_id": e["id"],
        "summary": e.get("summary", "No Title"),
        "start": e["start"].get("dateTime", e["start"].get("date")),
        # ✅ added end time
        "end": e["end"].get("dateTime", e["end"].get("date")),
    } for e in events]


# Reschedule using date + time (good for chatbot)
def update_event_time(event_id, new_start, new_end=None):
    """
    Reschedules an existing event in Google Calendar.
    new_start, new_end should be datetime objects
    """
    if new_end is None:
        new_end = new_start + datetime.timedelta(hours=1)  # default 1 hour

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    try:
        event = service.events().get(calendarId="primary", eventId=event_id).execute()
        event["start"]["dateTime"] = new_start.isoformat()
        event["end"]["dateTime"] = new_end.isoformat()

        updated_event = service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=event
        ).execute()

        return {
            "status": "Success",
            "event_id": event_id,
            "htmlLink": updated_event.get("htmlLink")
        }

    except Exception as e:
        return {"status": "Failed", "message": str(e)}

# Reschedule using datetime objects (good for backend logic)


def update_event(event_id, new_start, new_end):
    """
    Fully updates an event's start and end datetime.
    Works with datetime.datetime objects.
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    try:
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        event['start'] = {
            "dateTime": new_start.isoformat(),
            "timeZone": "Asia/Karachi",
        }

        event['end'] = {
            "dateTime": new_end.isoformat(),
            "timeZone": "Asia/Karachi",
        }

        updated_event = service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=event
        ).execute()

        return {
            "status": "Success",
            "event_id": event_id,
            "htmlLink": updated_event.get("htmlLink")
        }

    except Exception as e:
        return {"status": "Failed", "error": str(e)}

# Delete an event (delete_agent)


def delete_event(event_id):
    """
    Deletes an event from Google Calendar.
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    try:
        service.events().delete(
            calendarId="primary",
            eventId=event_id
        ).execute()

        return {
            "status": "Cancelled",
            "event_id": event_id
        }

    except Exception as e:
        return {
            "status": "Failed",
            "message": str(e)
        }

# Update event details (update_agent)


def update_event_details(event_id, updates):
    """
    Updates event fields like summary (topic), location, description.
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    try:
        event = service.events().get(
            calendarId="primary",
            eventId=event_id
        ).execute()

        if "topic" in updates:
            event["summary"] = updates["topic"]

        if "description" in updates:
            event["description"] = updates["description"]

        updated_event = service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=event
        ).execute()

        return {
            "status": "Updated",
            "event_id": event_id,
            "htmlLink": updated_event.get("htmlLink")
        }

    except Exception as e:
        return {
            "status": "Failed",
            "message": str(e)
        }


def is_time_slot_free(start_datetime, end_datetime, exclude_event_id=None):
    """
    Check if a given time slot is free in the user's calendar.
    exclude_event_id: ignore a specific event (useful for rescheduling)
    Returns True if free, False if there’s a clash.
    """
    events = list_upcoming_events(max_results=50)
    for e in events:
        if exclude_event_id and e["event_id"] == exclude_event_id:
            continue
        existing_start = datetime.datetime.fromisoformat(
            e["start"]).astimezone(PKT)
        existing_end = datetime.datetime.fromisoformat(
            e["end"]).astimezone(PKT)

        # check overlap
        if start_datetime < existing_end and end_datetime > existing_start:
            return False
    return True


def main():
    get_credentials()


if __name__ == "__main__":
    main()
