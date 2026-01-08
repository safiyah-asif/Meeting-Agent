import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
import uuid
from my_agents.Agent_manager import manager_agent
from my_agents.meeting_canceller import meeting_canceller_agent
from my_agents.meeting_rescheduler import meeting_rescheduler_agent
from my_agents.meeting_update import meeting_update_agent
from my_agents.meeting_scheduler import meeting_scheduler_agent
from my_agents.meeting_viewer import meeting_viewer_agent
from agents import Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, SQLiteSession
import nest_asyncio
from voice_input import render_voice_input

# --- Setup ---
nest_asyncio.apply()
load_dotenv()
set_tracing_disabled(disabled=False)

# --- OpenRouter Client ---
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# --- Model ---
model = OpenAIChatCompletionsModel(
    model="openai/gpt-4o-mini",
    openai_client=client
)

# --- Agents ---
viewer_agent_obj = meeting_viewer_agent(model=model)
scheduler_agent_obj = meeting_scheduler_agent(model=model)
canceller_agent_obj = meeting_canceller_agent(model=model)
rescheduler_agent_obj = meeting_rescheduler_agent(model=model)
updater_agent_obj = meeting_update_agent(model=model)

# --- Main Agent Manager ---
starting_agent = manager_agent(
    model=model,
    viewer=viewer_agent_obj,
    scheduler=scheduler_agent_obj,
    canceller=canceller_agent_obj,
    rescheduler=rescheduler_agent_obj,
    updater=updater_agent_obj,
)

# --- System Prompt ---
SYSTEM_PROMPT = """You are MeetingBot 🤖.
Handle scheduling, rescheduling, canceling, and updating meetings.
Ask one question at a time.
Be polite and concise.
"""

# --- Streamlit Setup ---
st.set_page_config(page_title="🚀 AI Meeting Assistant", layout="wide")
st.title("👋 Meeting Bot 🤖")

# --- Session State ---
if "memory" not in st.session_state:
    st.session_state.memory = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = SYSTEM_PROMPT

if "runner" not in st.session_state:
    st.session_state.runner = Runner()

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "db_session" not in st.session_state:
    st.session_state.db_session = SQLiteSession(
        st.session_state.conversation_id, "conversations.db"
    )

# --- Initial Greeting ---
if not st.session_state.memory:
    greeting = """👋 Hello! I'm your Meeting Bot 🤖.
I can help you with:
- Schedule a meeting
- Check your calendar
- Cancel or update a meeting
- Reschedule a meeting
How can I assist you today?
"""
    st.session_state.memory.append({"role": "assistant", "content": greeting})

# --- Helper: Process User Message ---


def process_user_message(user_msg: str):
    st.session_state.memory.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # --- Context trimming ---
    MAX_TOTAL_CHARS = 4096
    context_for_agent = [
        {"role": "system", "content": st.session_state.system_prompt}]
    total_chars = len(st.session_state.system_prompt)

    for msg in reversed(st.session_state.memory):
        msg_content = msg["content"] if isinstance(
            msg["content"], str) else str(msg["content"])
        msg_len = len(msg_content)
        if total_chars + msg_len > MAX_TOTAL_CHARS:
            break
        context_for_agent.append({"role": msg["role"], "content": msg_content})
        total_chars += msg_len

    context_for_agent = context_for_agent[:1] + context_for_agent[1:][::-1]

    # --- Run Agent ---
    with st.chat_message("assistant"):
        try:
            result = st.session_state.runner.run_sync(
                starting_agent=starting_agent,
                input=user_msg,
                context=context_for_agent,
                session=st.session_state.db_session
            )
            final_output = result.final_output
            st.write(final_output)
            st.session_state.memory.append(
                {"role": "assistant", "content": final_output})
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.memory.append(
                {"role": "assistant", "content": f"Sorry, I encountered an error: {e}"})


# --- Display Chat History ---
for msg in st.session_state.memory:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input Area ---
col1, col2 = st.columns([8, 1])

with col1:
    user_input = st.chat_input("Type your message here:")

with col2:
    mic_pressed = st.button("🎤")

# --- Handle Mic Input ---
if mic_pressed:
    with st.spinner("Recording for 8 seconds... Speak now!"):
        spoken_text = render_voice_input(duration=8)
    if spoken_text:
        process_user_message(spoken_text)

# --- Handle Text Input ---
if user_input:
    process_user_message(user_input)
