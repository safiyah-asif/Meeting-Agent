from agents import Agent, function_tool


@function_tool
def update_meeting(meeting_id, updates):
    """
    Updates meeting details. Updates should be a dict with keys like:
    topic, location, participants, etc.
    """
    return {
        "meeting_id": meeting_id,
        "status": "Updated",
        "updates": updates,
        "message": "Meeting updated successfully."
    }


def meeting_update_agent(model):
    return Agent(
        name="Meeting Updater",
        instructions="""
        You are a meeting update assistant.
        - Use update_meeting() when user wants to modify meeting details (topic, location, participants, etc.).
        - Ask for meeting ID and what needs to be updated if not provided.
        - Confirm updates in a polite tone.
        """,
        tools=[update_meeting],
        model=model
    )
