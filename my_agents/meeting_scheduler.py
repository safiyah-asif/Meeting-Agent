from agents import Agent, function_tool
from calendar_setup import create_event
import random
import datetime 


@function_tool
def schedule_meeting(organizer_name, participant_name, meeting_date, meeting_time, topic=None, location=None):
    """Schedules a meeting and returns confirmation details, also creates event in Google Calendar."""

    # Convert meeting_date and meeting_time strings to a datetime object
    # Assuming meeting_date format: 'YYYY-MM-DD' and meeting_time format: 'HH:MM'
    start_datetime = datetime.datetime.strptime(f"{meeting_date} {meeting_time}", "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + datetime.timedelta(hours=1)  # default 1-hour meeting

    # -------------------------
    # FIXED: Call Google Calendar API to create the actual event
    # -------------------------
    google_event = create_event(
        title=f"Meeting: {topic or 'General Discussion'}",
        description=f"Organizer: {organizer_name}\nParticipant: {participant_name}",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        location=location
    )

    meeting_id = f"M-{random.randint(1000, 9999)}"
    confirmation_msg = (
        f"✅ Meeting scheduled between {organizer_name} and {participant_name} "
        f"on {meeting_date} at {meeting_time}. "
        f"Topic: {topic or 'General Discussion'}; "
        f"Location: {location or 'Not specified'}\n"
        f"Google Calendar link: {google_event.get('htmlLink')}"
    )
    return {
        "meeting_id": meeting_id,
        "status": "Scheduled",
        "message": confirmation_msg
    }

def meeting_scheduler_agent(model):
    return Agent(
        name="Scheduler",
        instructions="""

        You are a scheduling assistant. Collect missing meeting details one by one:
        - organizer, participant, date, time, topic, location
        - Do not ask for details already provided
        - Ask short and clear questions
        - Once all required fields are collected, call the schedule_meeting() tool
        - Confirm with a clear message when the meeting is booked

        Always store collected fields in conversation memory so you don't ask again.

        Example flow:
        User: "I want to schedule a meeting."
        Agent: "Sure! Who is the organizer of the meeting?"
        User: "Alice"
        Agent: "Great! Who is the participant?"
        and so on...
        """,
        tools=[schedule_meeting],
        model=model
    )
