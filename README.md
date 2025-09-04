# Mini Chatbox AI

A minimal chatbot web app using **Flask + HTML/CSS/JS + SQLite**.

## 🧱 Project Structure
```
chatbox-ai-mini/
├─ app.py                 # Flask server & chat logic
├─ requirements.txt       # Python dependencies
├─ templates/
│  └─ index.html          # Chat UI
├─ static/
│  ├─ style.css           # Styling (modern glassmorphism UI)
│  └─ app.js              # Frontend logic (fetch API, render bubbles)
└─ data/
   ├─ intents.json        # Add your custom intents / replies
   └─ chat.db             # Auto-created SQLite DB for chat history
```

## ▶️ Run Locally
1) **Create venv & install deps**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

2) **Start the server**
```bash
python app.py
```
Then open http://localhost:5000

## 💾 File Handling (where things are stored)
- **`data/chat.db`**: SQLite database that stores every message with columns
  - `user_id` (string), `sender` ('user'/'bot'), `text` (message), `ts` (timestamp)
- **`data/intents.json`**: Define simple intents with `patterns` (keywords or `re:` regex) and a single `response`.
- **Static files** (CSS/JS) live in `static/`; HTML in `templates/` (Flask default).

## 🧠 Customize Bot Replies
Edit `data/intents.json`. Example:
```json
{
  "intents": [
    {
      "tag": "fees",
      "patterns": ["tuition fees", "semester fees", "re:fees?\\s*(structure|amount)"],
      "response": "Semester fees vary by department. Do you want the general breakdown or detailed?"
    }
  ]
}
```
> Restart the server after editing to reload intents.

## 🔐 Optional: Persist Users
Use the **User** input (top-right) to set `user_id`. All chats save under that ID and can be reloaded via the **History** button.

## 🧪 API Endpoints
- `POST /api/message`  JSON: `{"message": "...", "user_id": "guest"}` → `{"ok": true, "reply": "..."}`
- `GET  /api/history?user_id=guest` → complete chat log for the user.

## 🚀 Ideas to Upgrade
- Add JWT login & user accounts
- Plug in an external LLM API
- Train an FAQ embedding search (e.g., sentence-transformers) for smarter answers
- Add voice input/output in the frontend (Web Speech API)
- Export chat history as CSV

## 🧹 Reset / Remove History
Stop the server and delete `data/chat.db` (a fresh DB is created on next run).
"# mini-chatbox-ai" 
