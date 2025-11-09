import os
from dotenv import load_dotenv
import chainlit as cl
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from calendar_setup import get_upcoming_events


load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo"),
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)


TEMPLATE = """
You are MeetingBot 🤖 — a friendly assistant that helps manage meetings.
You can:
- Schedule, reschedule, or cancel meetings
- Show calendar events
- Answer politely and concisely

Chat history:
{history}

User: {input}
Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=TEMPLATE
)

# In-memory session storage for chat history
session_memory = {}


@cl.on_chat_start
async def start():
    user_id = cl.user_session.get("id")  # Unique session id
    session_memory[user_id] = ConversationBufferMemory(return_messages=True)

    greeting = """👋 Hello! I'm your Meeting Bot 🤖  
I can help you with:
- Schedule a meeting  
- Check your calendar  
- Cancel or update a meeting  
- Reschedule a meeting  

How can I assist you today?
"""
    session_memory[user_id].append({"role": "assistant", "content": greeting})
    await cl.Message(content=greeting).send()


@cl.on_message
async def main(message: cl.Message):
    user_id = cl.user_session.get("id")

    # Get or create session memory
    if user_id not in session_memory:
        session_memory[user_id] = ConversationBufferMemory(
            return_messages=True)

    memory = session_memory[user_id]
    user_input = message.content.strip()

    # Check if user wants to see events
    if "show" in user_input.lower() and "event" in user_input.lower():
        await cl.Message(content="🔄 Fetching your upcoming events...").send()
        events = get_upcoming_events()
        if not events:
            reply = "No upcoming events found."
        else:
            reply = "\n".join(
                [f"📅 {start} — {summary}" for start, summary in events])
        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(reply)
        await cl.Message(content=reply).send()
        return

    # Build conversation-aware prompt
    history = "\n".join(
        [f"{msg.type.capitalize()}: {msg.content}" for msg in memory.chat_memory.messages]
    )
    formatted_prompt = prompt.format(history=history, input=user_input)

    # Get LLM response
    response = llm(formatted_prompt)

    # Update memory
    memory.chat_memory.add_user_message(user_input)
    memory.chat_memory.add_ai_message(response.content)

    # Send response
    await cl.Message(content=response.content).send()
