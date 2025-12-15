from agents import Agent, function_tool
from calendar_setup import delete_event

@function_tool
def cancel_meeting(event_id, reason=None):
    """Cancels a meeting from Google Calendar."""
    result = delete_event(event_id)

    if result["status"] == "Failed":
        return {
            "status": "Failed",
            "event_id": event_id,
            "message": result["message"]
        }

    return {
        "meeting_id": event_id,
        "status": "Cancelled",
        "reason": reason or "Not specified",
        "message": "✅ Meeting cancelled successfully."
    }


def meeting_canceller_agent(model):
    return Agent(
        name="Meeting Canceller",
        instructions="""
        You are a meeting cancellation assistant.
        - Use cancel_meeting() when user wants to cancel or reschedule a meeting.
        - Ask for meeting ID and reason if not provided.
        - Confirm cancellation in a polite tone.
        """,
        tools=[cancel_meeting],
        model=model
    )
