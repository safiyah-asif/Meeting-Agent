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


def get_upcoming_events():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=5,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    event_list = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        event_list.append((start, event.get("summary", "No Title")))
    return event_list


def main():
    creds = None  # credentials is none because right now it does not have permission to access google account

    if os.path.exists("token.json"):
        # this loads the save credentials from the file so that the user does not have to re-authorize on every run
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.refresh_token:
            # If there is no new token it will automatically get new access tokens without user interaction
            creds.refresh(Request())

        # In else condition it is checking if there is no credentials meaning it is running for the first time
        else:
            # It will ask user to login into your google account, and after login it will send back new credentials
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        # It will create a token.json file where it will write ("w") new content
        with open("token.json", "w") as token:
            # to_json will convert the credentials to json string
            token.write(creds.to_json())

    # It creates a google calendar API
    service = build("calendar", "v3", credentials=creds)


if __name__ == "__main__":
    main()
