from agents import Agent, function_tool
import random


@function_tool
def schedule_meeting(organizer_name, participant_name, meeting_date, meeting_time, topic=None, location=None):
    """Schedules a meeting and returns confirmation details."""
    meeting_id = f"M-{random.randint(1000, 9999)}"
    confirmation_msg = (
        f"✅ Meeting scheduled between {organizer_name} and {participant_name} "
        f"on {meeting_date} at {meeting_time}. "
        f"Topic: {topic or 'General Discussion'}"
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
        You are a scheduling assistant.
        - Use schedule_meeting() when user requests to arrange, set, plan, or book a meeting.
        - Collect details like organizer, participant, date, time, topic, and location if missing.
        - Confirm once meeting is booked.
        """,
        tools=[schedule_meeting],
        model=model
    )
