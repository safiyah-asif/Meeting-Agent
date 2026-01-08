# 🤖 Meeting Agent – Conversational AI Meeting Assistant

A **purely conversational AI meeting assistant** built with **Streamlit**, **agent-based orchestration**, and **Google Calendar integration**.  
This project allows users to **schedule, update, reschedule, and cancel meetings** through **natural language conversations**, without requiring meeting IDs or UI-based selection.

---

## ✨ Key Features

- 💬 **Fully Conversational Interface** (no dropdowns, no forms)
- 📅 **Google Calendar Integration**
- 🧠 **Multi-Agent Architecture**
  - Scheduler Agent
  - Canceller Agent
  - Rescheduler Agent
  - Updater Agent
  - Manager Agent (intent router)
- 🔁 **Context-Aware Conversations**
- ❌ No need for users to know meeting IDs
- 📡 Uses **Gemini (Google Generative AI)** via OpenAI-compatible API

---

---

## 🧠 Conversational Flow (How It Works)

### Example: Cancel a Meeting

**User:**

> Cancel my meeting tomorrow

**Agent:**

> I found two meetings tomorrow:
>
> 1. Project Sync at 10:00 AM
> 2. Design Review at 3:00 PM
>
> Which one would you like to cancel?

**User:**

> 2.

✔ The agent resolves the correct meeting internally  
✔ The user never sees or provides an event ID

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit**
- **Google Calendar API**
- **openai/gpt-4o-mini**
- **OpenAI-compatible Agents SDK**
- **Async Programming (asyncio)**

---

## ⚙️ Virtual Environment (venv) Setup

```bash
1️⃣ Create Virtual Environment
python -m venv venv

2️⃣ Activate Virtual Environment
Windows
.\.venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

```

## ▶️ Running the Application

```bash
streamlit run main.py
```

## 🧩 Supported Conversational Intents

| Intent     | Description                  |
| ---------- | ---------------------------- |
| Schedule   | Create a new meeting         |
| Cancel     | Cancel an existing meeting   |
| Reschedule | Change meeting date/time     |
| Update     | Change topic or participants |

---

## 🔁 Update Rules (Enforced by Agent)

- ✅ Change meeting topic/title
- ➕ Add participant
- ➖ Remove participant
- ❌ No location or description updates

---

## 🧪 Example Prompts to Try

- “Schedule a meeting with Ali 1 JAN 2026 at 4 PM”
- “Cancel my meeting”
- “Reschedule the project sync to Friday”
- “Add John to the design meeting”
- “Change the topic of tomorrow’s meeting”

---

## 🔒 Design Principles

- Event IDs are system-only
- Users interact naturally
- One question at a time
- No hallucinated meetings
- Agent-driven disambiguation

---

## 🚀 Future Enhancements

- 📧 Email invitations
- ⏰ Smart time suggestions
- 📊 Meeting analytics
- 🗣️ Voice input support

---
