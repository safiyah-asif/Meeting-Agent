from tracemalloc import start
from agents import Agent, function_tool
from calendar_setup import create_event
from calendar_tools import check_slot_free
import random
import datetime
from email_utils import send_email

PKT = datetime.timezone(datetime.timedelta(hours=5))


@function_tool
def schedule_meeting(organizer_name: str,
                     participants: list | None,
                     participant_name: str | None = None,
                     participant_email: str | None = None,
                     meeting_date: str = None,
                     meeting_time: str = None,
                     topic: str | None = None):
    """Schedules a meeting, creates event in Google Calendar, and sends confirmation emails.

    Accepts either:
    - `participants`: a list of dicts [{"name": ..., "email": ...}, ...]
    OR
    - `participant_name` and `participant_email` for a single participant (backwards compatibility).
    """

    def normalize_time(time_str):
        try:
            return datetime.datetime.strptime(time_str.strip(), "%H:%M").time()
        except ValueError:
            return datetime.datetime.strptime(time_str.strip(), "%I:%M %p").time()

    # Normalize participants input
    if participants is None:
        if participant_name and participant_email:
            participants_list = [
                {"name": participant_name, "email": participant_email}]
        else:
            return {"status": "Failed", "message": "No participants provided."}
    else:
        participants_list = participants

    # 🔧 FIX 2: Parse date safely
    if not meeting_date:
        return {"status": "Failed", "message": "meeting_date is required"}
    # Parse and validate meeting date
    try:
        date_obj = datetime.datetime.strptime(meeting_date.strip(), "%Y-%m-%d").date()
        # Ensure date is not in the past
        if date_obj < datetime.datetime.now(PKT).date():
            return {"status": "Failed", "message": "Meeting date cannot be in the past."}
    except ValueError:
        return {"status": "Failed", "message": "Invalid date format. Please use YYYY-MM-DD format."}

    # 🔧 FIX 3: Build datetime correctly
    time_obj = normalize_time(meeting_time)
    start = datetime.datetime.combine(date_obj, time_obj, tzinfo=PKT)
    end = start + datetime.timedelta(hours=1)

    # 🔧 FIX 4: Clash check
    if not check_slot_free(start, end):
        return {"status": "Failed", "message": "Time slot clashes with another meeting."}

    # -------------------------
    # FIXED: Call Google Calendar API to create the actual event
    # -------------------------

    # Prepare attendees for Google Calendar
    attendees = []
    for p in participants_list:
        attendees.append({"email": p.get("email"), "name": p.get("name")})

    google_event = create_event(
        title=f"Meeting: {topic or 'General Discussion'}",
        description=(f"Organizer: {organizer_name}\n" +
                     "Participants:\n" +
                     "\n".join([f"- {p.get('name')} <{p.get('email')}>" for p in participants_list])),
        start_datetime=start,
        end_datetime=end,
        attendees=attendees
    )

    meeting_id = f"M-{random.randint(1000, 9999)}"
    confirmation_msg = (
        f"✅ Meeting scheduled successfully!\n"
        f"📅 Date: {meeting_date}\n"
        f"⏰ Time: {meeting_time} PKT\n"
        f"google_event_id: {google_event.get('event_id')}\n"
        f"🔗 Google Calendar: {google_event.get('htmlLink')}"
    )

    # Send emails to all participants and collect results
    email_subject = f"Meeting Scheduled: {topic or 'Discussion'} on {meeting_date}"
    email_results = []
    for p in participants_list:
        name = p.get("name")
        email = p.get("email")
        email_body = (
            f"Hello {name},\n\n"
            f"You have been invited to a meeting. Here are the details:\n\n"
            f"Organizer: {organizer_name}\n"
            f"Topic: {topic or 'General Discussion'}\n"
            f"Date: {meeting_date}\n"
            f"Time: {meeting_time} PKT\n"
            f"Regards,\nMeeting Bot"
        )
        res = send_email(email, email_subject, email_body)
        email_results.append({"email": email, "result": res})

    return {
        "meeting_id": meeting_id,
        "status": "Scheduled",
        "message": confirmation_msg,
        "google_event": google_event,
        "email_results": email_results,
    }


def meeting_scheduler_agent(model):
    return Agent(
        name="Scheduler",
        instructions="""

        You are a scheduling assistant. Your goal is to collect all necessary details (organizer_name, participant_name, meeting_date, meeting_time, topic) to call the schedule_meeting() tool.

        **CRITICAL:** Review the entire conversation history (provided in the context) to identify and extract any details already given by the user.

        - **Do not ask for details already provided in the history.**
        - Ask for missing details one by one.
        - Ask short and clear questions.
        - When there are multiple participants, collect a list of participant names and emails (e.g., name<email@example.com>), or ask for them one-by-one.
        - Once all required fields are collected, call the schedule_meeting() tool with `participants` as a list of objects: [{"name":..., "email":...}, ...].
        - Confirm with a clear message when the meeting is booked.
        - Accept time in both 24-hour (11:00) and 12-hour (11:00 AM) formats.
        - Never ask the user to reconfirm time format once provided.
        - Normalize time internally before calling the tool.

        Example flow:
        User: "I want to schedule a meeting with Alice."
        Agent: "Sure! Who is the organizer of the meeting?"
        User: "It's me, Bob. The meeting should be tomorrow."
        Agent: "I see. What specific time on tomorrow would you like the meeting to start? (e.g., 10:00)"

        """,
        tools=[schedule_meeting],
        model=model
    )
