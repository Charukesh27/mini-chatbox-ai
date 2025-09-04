from flask import Flask, render_template, request, jsonify, g
from datetime import datetime
import sqlite3
import re
import json
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "data", "chat.db")
INTENTS_PATH = os.path.join(APP_DIR, "data", "intents.json")

app = Flask(__name__)

# ---------------------- Database ----------------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    con = get_db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            sender TEXT CHECK(sender IN ('user','bot')) NOT NULL,
            text TEXT NOT NULL,
            ts TEXT NOT NULL
        );
    """)
    con.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# ---------------------- Intents ----------------------
def load_intents():
    if not os.path.exists(INTENTS_PATH):
        return []
    with open(INTENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("intents", [])

INTENTS = load_intents()

def match_intent(message: str):
    msg = message.lower().strip()
    # Exact / simple keyword rules first
    rules = [
        (r"\b(hi|hello|hey|hola|vanakkam)\b", "Hello! 👋 How can I help you today?"),
        (r"\bhow are you\b", "I’m doing great! Thanks for asking 😊 How about you?"),
        (r"\b(your )?name\b", "I’m Mini Chatbox AI. Nice to meet you!"),
        (r"\b(bye|goodbye|see you)\b", "Bye! 👋 Have a great day!"),
        (r"\b(thanks|thank you|thanku)\b", "You're welcome! 🙌 Anything else I can help with?"),
        (r"\bhelp\b", "Sure! You can ask me about greetings, time, date, simple facts, or just chat 🙂"),
        (r"\b(date|today)\b", f"Today's date is {datetime.now().strftime('%Y-%m-%d')}."),
        (r"\btime\b", f"The current time is {datetime.now().strftime('%H:%M:%S')}."),
        (r"\bjoke\b", "Here’s one: Why did the developer go broke? Because he used up all his cache 😄"),
    ]
    for pat, resp in rules:
        if re.search(pat, msg):
            return resp

    # Try JSON-defined intents (patterns as regex or keywords)
    for intent in INTENTS:
        patterns = intent.get("patterns", [])
        for pat in patterns:
            try:
                if pat.startswith("re:"):
                    if re.search(pat[3:], msg):
                        return intent.get("response", "I’m here to help!")
                else:
                    # keyword match
                    if pat.lower() in msg:
                        return intent.get("response", "I’m here to help!")
            except re.error:
                continue

    # Fallback
    return "I didn’t quite get that 🤔. Try asking me about time, date, a joke, or say 'help'."

def save_message(user_id: str, sender: str, text: str):
    con = get_db()
    con.execute(
        "INSERT INTO messages (user_id, sender, text, ts) VALUES (?, ?, ?, ?)",
        (user_id, sender, text, datetime.now().isoformat(timespec='seconds'))
    )
    con.commit()

# ---------------------- Routes ----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/message", methods=["POST"])
def api_message():
    payload = request.get_json(force=True)
    message = (payload.get("message") or "").strip()
    user_id = (payload.get("user_id") or "guest").strip() or "guest"

    if not message:
        return jsonify({"ok": False, "error": "Empty message"}), 400

    init_db()  # ensure DB exists
    save_message(user_id, "user", message)

    reply = match_intent(message)
    save_message(user_id, "bot", reply)

    return jsonify({"ok": True, "reply": reply})

@app.route("/api/history", methods=["GET"])
def api_history():
    user_id = (request.args.get("user_id") or "guest").strip() or "guest"
    init_db()
    con = get_db()
    rows = con.execute(
        "SELECT sender, text, ts FROM messages WHERE user_id = ? ORDER BY id ASC",
        (user_id,)
    ).fetchall()
    history = [dict(r) for r in rows]
    return jsonify({"ok": True, "history": history})

if __name__ == "__main__":
    os.makedirs(os.path.join(APP_DIR, "data"), exist_ok=True)
    with app.app_context():
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
