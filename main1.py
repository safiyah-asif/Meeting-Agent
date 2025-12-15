import asyncio
import os
import streamlit as st
import asyncio
from dotenv import load_dotenv
from my_agents.Agent_manager import manager_agent
from my_agents.meeting_canceller import meeting_canceller_agent
from my_agents.meeting_rescheduler import meeting_rescheduler_agent
from my_agents.meeting_update import meeting_update_agent
from my_agents.meeting_scheduler import meeting_scheduler_agent
from agents import Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
from calendar_setup import list_upcoming_events, reschedule_event, update_event_time
import nest_asyncio
import datetime
nest_asyncio.apply()

load_dotenv()
set_tracing_disabled(disabled=False)

api = os.getenv('GOOGLE_API_KEY')
client = AsyncOpenAI(
    api_key=api,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Create Gemini model instance
model = OpenAIChatCompletionsModel(
    model='gemini-2.5-flash',
    openai_client=client
)

# Create Agents
scheduler_agent_obj = meeting_scheduler_agent(model=model)
canceller_agent_obj = meeting_canceller_agent(model=model)
rescheduler_agent_obj = meeting_rescheduler_agent(model=model)
updater_agent_obj = meeting_update_agent(model=model)


# main agent
starting_agent = manager_agent(
    model=model,
    scheduler=scheduler_agent_obj,
    canceller=canceller_agent_obj,
    rescheduler=rescheduler_agent_obj,
    updater=updater_agent_obj,
)


st.set_page_config(page_title="🚀 AI Meeting Assistant", page_icon="🌍")
st.title("👋 Meeting Bot 🤖")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "runner" not in st.session_state:
    st.session_state.runner = Runner()

if "active_flow" not in st.session_state:
    st.session_state.active_flow = None
# if not st.session_state.chat_history:
#     greeting = """You are MeetingBot 🤖 — a friendly assistant that helps manage meetings.
#     You can handle:
#     - ✅ Schedule a meeting
#     - 🔄 Reschedule a meeting
#     - ❌ Cancel a meeting
#     - 📝 Update a meeting
#     Answer politely and concisely.
#     When taking information , ask one question at a time.
#     Carefully ask complete information as instructed and given in tool functions.
#     """

if not st.session_state.chat_history:
    greeting = """👋 Hello! I'm your Meeting Bot 🤖.\n
    I can help you with:\n
    - ✅ Schedule a meeting \n
    - 🔄 Reschedule a meeting \n
    - ❌ Cancel a meeting \n
    - 📝 Update a meeting \n
    How can I assist you today?"""
    st.session_state.chat_history.append(
        {"role": "assistant", "content": greeting})

# display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ INTENT DETECTION ------------------


def detect_intent(text: str):
    text = text.lower()
    if any(x in text for x in ["schedule", "set up", "book meeting"]):
        return "schedule"
    if any(x in text for x in ["cancel", "delete"]):
        return "cancel"
    if any(x in text for x in ["reschedule", "move"]):
        return "reschedule"
    if any(x in text for x in ["update", "modify"]):
        return "update"
    return None


# Chat input
if user_msg := st.chat_input("Type your message here:"):
    if user_msg.strip():
        # Save user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_msg}
        )

        with st.chat_message("user"):
            st.markdown(user_msg)

        with st.chat_message("assistant"):
            if st.session_state.active_flow == "schedule":
                result = st.session_state.runner.run_sync(
                    starting_agent=scheduler_agent_obj,
                    input=user_msg,
                    context=st.session_state.chat_history,
                )

            else:
                # detect intent only ONCE
                intent = detect_intent(user_msg)

                if intent == "schedule":
                    st.session_state.active_flow = "schedule"

                result = st.session_state.runner.run_sync(
                    starting_agent=starting_agent,
                    input=user_msg,
                    context=st.session_state.chat_history,
                )

            response = result.final_output
            st.markdown(response)

        # save assistant msg
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )


# --- Conditional Reschedule UI ---
show_reschedule_ui = any(
    "reschedule" in m["content"].lower()
    for m in st.session_state.chat_history
    if m["role"] == "user"
)

if show_reschedule_ui:
    # Reschedule UI Section
    st.markdown("---")
    st.header("🗓️ Google Calendar Meeting Rescheduler")
    st.write("select a meeting and choose a new date & time")

    # Load upcoming events
    events = list_upcoming_events()
    if not events:
        st.warning("No upcoming meetings found.")
    else:
        event_options = {
            f"{e['summary']} — {e['start']}": e["event_id"] for e in events
        }

        selected_label = st.selectbox(
            "Choose a meeting to reschedule:", list(event_options.keys()))
        selected_event_id = event_options[selected_label]
        st.write(f"Selected Event ID: {selected_event_id}")

        # New date & time
        new_date = st.date_input("New Date", datetime.date.today())
        new_time = st.time_input("New Time", datetime.time(9, 0))
        new_start = datetime.datetime.combine(new_date, new_time)
        new_end = new_start + datetime.timedelta(hours=1)

        if st.button("Reschedule Meeting"):
            with st.spinner("Rescheduling meeting..."):
                result = reschedule_event(
                    selected_event_id, new_start, new_end)

            if result["status"] == "Success":
                st.success("Meeting rescheduled successfully!")
                st.markdown(f"[Open in google calendar]({result['htmlLink']})")
            else:
                st.error(
                    f"Failed to reschedule meeting: {result.get('error', 'Unknown error')}")
                st.code(result["error"])
