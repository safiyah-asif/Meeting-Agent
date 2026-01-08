from calendar_setup import list_upcoming_events, list_meetings_for_selection
import datetime

PKT = datetime.timezone(datetime.timedelta(hours=5))


def get_upcoming_meetings(max_results=10):
    return list_upcoming_events(max_results=max_results)


def check_slot_free(new_start, new_end, exclude_event_id=None):
    """Check if a given time slot is free in the calendar."""
    events = list_upcoming_events(max_results=50)
    for e in events:
        if exclude_event_id and e["event_id"] == exclude_event_id:
            continue
        existing_start = datetime.datetime.fromisoformat(
            e["start"]).astimezone(PKT)
        existing_end = datetime.datetime.fromisoformat(
            e["end"]).astimezone(PKT)
        if new_start < existing_end and new_end > existing_start:
            return False
    return True


def resolve_meeting_by_index(index: int):
    meetings = list_meetings_for_selection()
    for m in meetings:
        if m["index"] == index:
            return m["event_id"]  # ⚡ return actual event ID
    return None


