from agents import Agent, function_tool
from calendar_setup import create_event
import random
import datetime

# we should add a Pydantic model here to validate inputs
# class BookingRequest(BaseModel):
#     """Data model for booking requests."""
#     customer_name: str = Field(description="Customer's full name")
#     customer_email: str = Field(description="Customer's email address")
#     meeting_title: str = Field(description="Title or purpose of the meeting")
#     date: str = Field(description="Meeting date in YYYY-MM-DD format")
#     start_time: str = Field(
#         description="Meeting start time in HH:MM format (24-hour)")
#     duration_min: int = Field(
#         default=30, description="Meeting duration in minutes (15-240)")
#     notes: str = Field(default="", description="Optional meeting notes")


@function_tool
def schedule_meeting(organizer_name, participant_name, participant_email, meeting_date, meeting_time, duration_min, topic=None, location=None):
    """Schedules a meeting and returns confirmation details, also creates event in Google Calendar.
        Args:
            participant_name: Participant's full name
            participant_email: PArticipant's email
            Topic: Meeting title/purpose
            meeting_date: Date in YYYY-MM-DD format
            meeting_time: Start time in HH:MM format
            duration_min: Duration in minutes (15-240)"""

    # Convert meeting_date and meeting_time strings to a datetime object
    # Assuming meeting_date format: 'YYYY-MM-DD' and meeting_time format: 'HH:MM'
    start_datetime = datetime.datetime.strptime(
        f"{meeting_date} {meeting_time}", "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + \
        datetime.timedelta(hours=1)  # default 1-hour meeting

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
        You are a friendly meeting scheduler assistant.
        Follow these steps to schedule a meeting:
        
        1. Ask the organizer's name if not provided.
        2. Ask for the meeting date.
        3. Ask for the meeting start time.
        4. Ask for duration or end time.
        5. Ask for participants.
        6. Once all info is collected, confirm details with the user.
        7. Then schedule the meeting using the calendar API.

        Always ask **one question at a time**.
        Keep track of answers in memory so you can reference them in the next step.
        """,
        tools=[schedule_meeting],
        model=model
    )
