from agents import function_tool
from calendar_setup import list_meetings_for_selection

def show_meeting_selection():
    """
    Returns a formatted list of upcoming meetings for user selection.
    Used by cancel, reschedule, update agents.
    """
    meetings = list_meetings_for_selection()
    if not meetings:
        return {
            "status": "Failed",
            "message": "No upcoming meetings found."
        }

    message = "Here are your upcoming meetings:\n"
    for m in meetings:
        message += f"{m['index']}) {m['label']}\n"

    message += "\nPlease select the number of the meeting."
    return message