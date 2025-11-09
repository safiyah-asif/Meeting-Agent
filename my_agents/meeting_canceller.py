from agents import Agent, function_tool

@function_tool
def cancel_meeting(meeting_id, reason=None):
    """Cancels a meeting by ID."""
    return {
        "meeting_id": meeting_id,
        "status": "Cancelled",
        "reason": reason or "Not specified",
        "message": "Meeting cancelled successfully."
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
