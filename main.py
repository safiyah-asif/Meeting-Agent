import os
from dotenv import load_dotenv
import streamlit as st
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
from calendar_setup import get_upcoming_events
import nest_asyncio

from my_agents import (
    manager_agent,
    meeting_scheduler_agent,
    meeting_canceller_agent,
    meeting_rescheduler_agent,
    meeting_update_agent,
)

nest_asyncio.apply()
load_dotenv()
set_tracing_disabled(disabled=False)

# ------------------ Setup Gemini Client ------------------
external_client = AsyncOpenAI(
    api_key=os.environ.get("GOOGLE_API_KEY"),
    base_url=os.environ.get(
        "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
    ),
)

llm_model = OpenAIChatCompletionsModel(
    model=os.environ.get("LLM_MODEL_NAME", "gemini-2.5-flash"),
    openai_client=external_client,
)

# ------------------ In-memory session storage ------------------
if "session_memory" not in st.session_state:
    st.session_state["session_memory"] = {}

# ------------------ Streamlit App ------------------
st.title("👋 Meeting Bot 🤖")
st.write(
    """
I can help you with:
- Schedule a meeting  
- Check your calendar  
- Cancel or update a meeting  
- Reschedule a meeting  

How can I assist you today?
"""
)

# User input
user_input = st.text_input("Type your message here:")

if user_input:
    user_id = "default_user"  # Streamlit doesn't have user sessions, so we use a default ID
    if user_id not in st.session_state["session_memory"]:
        st.session_state["session_memory"][user_id] = []

    # Store user input
    st.session_state["session_memory"][user_id].append({"role": "user", "content": user_input})

    # Handle “show events”
    if "show" in user_input.lower() and "event" in user_input.lower():
        st.write("🔄 Fetching your upcoming events...")
        events = get_upcoming_events()
        if not events:
            reply = "No upcoming events found."
        else:
            reply = "\n".join([f"📅 {start} — {summary}" for start, summary in events])
        st.session_state["session_memory"][user_id].append({"role": "assistant", "content": reply})
        st.write(reply)
    else:
        # Build messages for Gemini (include conversation history)
        messages_for_gemini = st.session_state["session_memory"][user_id]

        # Call Gemini LLM
        response = llm_model.completions.create(
            messages=messages_for_gemini,
            temperature=0.3,
        )

        assistant_reply = response.choices[0].message["content"]
        st.session_state["session_memory"][user_id].append({"role": "assistant", "content": assistant_reply})

        # Display assistant reply
        st.write(assistant_reply)