from agents import Agent, function_tool
from calendar_setup import reschedule_event
import random


@function_tool
def reschedule_meeting(event_id, new_date, new_time, reason=None):
    """Reschedules an existing meeting to new date and time."""
    result = reschedule_event(event_id, new_date, new_time)

    if result["status"] == "Failed":
        return{
            "status": "Failed",
            "event_id": event_id,
            "reason": reason or "Not specified",
            "message": result["message"]
        }
    
    return {
        "event_id": event_id,
        "status": "Rescheduled",
        "new_date": new_date,
        "new_time": new_time,
        "reason": reason or "Not specified",
        "calendar_link": result["htmlLink"],
        "message": f"Meeting rescheduled to {new_date} at {new_time}."
    }


def meeting_rescheduler_agent(model):
    return Agent(
        name="Meeting Rescheduler",
        instructions="""
        You are a meeting rescheduling assistant.
        - Use reschedule_meeting() when user wants to change meeting date/time.
        - Ask for meeting ID, new date, new time, and reason if not provided.
        - Confirm rescheduling in a polite tone.
        """,
        tools=[reschedule_meeting],
        model=model
    )
