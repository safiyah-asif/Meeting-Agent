from __future__ import print_function
import datetime
import os.path
from google.auth.transport.requests import Request
# Imports the class that holds and refreshes your Google login tokens, letting your app securely access APIs like Google Calendar
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build



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
            flow = InstalledAppFlow.from_client_secrets_file("D:/Eishal Work/6th Semester/Meeting-Agent/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save new credentials    
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds    
    
# Create an event in Google Calendar
def create_event(title, description, start_datetime, end_datetime, location=None):
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

    # Try inserting the event and catch errors
    try:
        created_event = service.events().insert(calendarId="primary", body=event).execute()
    except Exception as e:
        print("Error creating event:", e)
        return {"status": "Failed", "message": str(e)}

    return {
        "event_id": created_event.get("id"),
        "htmlLink": created_event.get("htmlLink"),
        "status": "Created"

    }

# List upcoming events
def list_upcoming_events(max_results=10):
    creads = get_credentials()
    service = build("calendar", "v3", credentials=creads)

    events_result = service.events().list(
        calendarId="primary",
        maxResults = max_results,
        singleEvents = True,
        orderBy = "startTime"   
    ).execute()

    events = events_result.get("items", [])

    return[ {
        "event_id": e["id"],
        "summary": e.get("summary", "No Title"),
        "start": e["start"].get("dateTime", e["start"].get("date")),
        
    } for e in events ]
    


# Reschedule using date + time (good for chatbot)
def update_event_time(event_id, new_date, new_time):
    """
    Reschedules an existing event in Google Calendar by updating its start and end time.
    new_start_datetime and new_end_datetime should be in datetime objects.

    """
    new_datetime = f"{new_date}T{new_time}:00"

    creads = get_credentials()
    service = build("calendar", "v3", credentials=creads)

    try:
        # get existing event
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        # update start and end time
        event["start"]["dateTime"] = new_datetime
        event["end"]["dateTime"] = new_datetime  # assuming 1-hour meeting

        updated_event = service.events().update(
            calendarId="primary", 
            eventId=event_id, 
            body=event
            ).execute()
        
        return{
            "status": "Success",
            "event_id": event_id,
            "new_datetime": new_datetime,
            "htmlLink": updated_event.get("htmlLink")
        }
    
    except Exception as e:
        return{
            "status": "Failed",
            "message": str(e)
        }

# Reschedule using datetime objects (good for backend logic)
def reschedule_event(event_id, new_start, new_end):
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

        return{
            "status": "Success",
            "event_id": event_id,
            "htmlLink": updated_event.get("htmlLink")
        }
    
    except Exception as e:
        return {"status": "Failed", "error": str(e)}
    

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

        if "location" in updates:
            event["location"] = updates["location"]

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


def main():
    get_credentials()

if __name__ == "__main__":
    main()
