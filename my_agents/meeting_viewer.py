from agents import Agent, function_tool
from meeting_selector import show_meeting_selection

@function_tool
def view_upcoming_meetings():
    """
    Returns upcoming meetings in a readable format for viewing only.
    DO NOT ask the user to select a meeting number.
    """
    return show_meeting_selection()


def meeting_viewer_agent(model):
    return Agent(
        name="Meeting Viewer",
        instructions="""
        You are a Google Calendar assistant specialized in showing upcoming meetings.
        - When the user asks about their meetings, display the list of upcoming meetings.
        - Do not ask for any other input.
        - Use show_meeting_selection() to get and display meetings.
        - Format the output nicely with numbers for each meeting.
        - Inform the user if there are no upcoming meetings.
        """,
        tools=[view_upcoming_meetings],
        model=model
    )