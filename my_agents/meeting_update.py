from agents import Agent, function_tool
from calendar_setup import update_event_details


@function_tool
def update_meeting(event_id, updates):
    """
    Updates meeting details such as topic or location.
    """
    result = update_event_details(event_id, updates)

    if result["status"] == "Failed":
        return {
            "status": "Failed",
            "event_id": event_id,
            "message": result["message"]
        }

    return {
        "meeting_id": event_id,
        "status": "Updated",
        "updates": updates,
        "calendar_link": result.get("htmlLink"),
        "message": "✅ Meeting updated successfully."
    }


def meeting_update_agent(model):
    return Agent(
        name="Meeting Updater",
        instructions="""
        You are a meeting update assistant.
        - Use update_meeting() when user wants to modify meeting details (topic, location, participants, etc.).
        - Ask for meeting ID and what needs to be updated if not provided.
        - Supported updates: topic, location, description.
        - Confirm updates in a polite tone.
        """,
        tools=[update_meeting],
        model=model
    )
