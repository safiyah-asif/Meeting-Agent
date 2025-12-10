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
import nest_asyncio
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
canceller_agent_obj = meeting_canceller_agent(model=model)
rescheduler_agent_obj = meeting_rescheduler_agent(model=model)
updater_agent_obj = meeting_update_agent(model=model)
scheduler_agent_obj = meeting_scheduler_agent(model=model)


# main agent
starting_agent = manager_agent(
    model=model, canceller=canceller_agent_obj, rescheduler=rescheduler_agent_obj, updater=updater_agent_obj, scheduler=scheduler_agent_obj)


st.set_page_config(page_title="🚀 AI Meeting Assistant", page_icon="🌍")
st.title("👋 Meeting Bot 🤖")

if "memory" not in st.session_state:
    st.session_state.memory = []
if "manager" not in st.session_state:
    st.session_state.manager = """You are MeetingBot 🤖 — a friendly assistant that helps manage meetings.
    You can handle:
    - ✅ Schedule a meeting
    - 🔄 Reschedule a meeting  
    - ❌ Cancel a meeting
    - 📝 Update a meeting
    Answer politely and concisely.
    When taking information , ask one question at a time.
    Carefully ask complete information as instructed and given in tool functions.
    """

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

for msg in st.session_state.memory:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if "runner" not in st.session_state:
    st.session_state.runner = Runner()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if user_msg := st.chat_input("Type your message here:"):
    # Save user input to history
    if user_msg and user_msg.strip():
        st.session_state.memory.append({"role": "user", "content": user_msg})

        # Show User Message in the Chatclear
        with st.chat_message("user"):
            st.markdown(user_msg)

        # Stream the agent’s reply
        with st.chat_message("assistant"):
            placeholder = st.empty()
            partial = ""

            result = st.session_state.runner.run_sync(
                starting_agent=starting_agent,
                input=user_msg,
                context=st.session_state.messages  # << your conversation history
            )

            final_output = result.final_output
            st.write(final_output)
            st.session_state.messages.append(
                {"role": "assistant", "content": final_output})
