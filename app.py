import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort

# -------------------- APP CONFIG --------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_fallback_key")

DATABASE = "tracker.db"


# -------------------- DB UTILITIES --------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Ensure required tables exist"""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            module TEXT NOT NULL,
            minutes INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# -------------------- ROUTES --------------------

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    today = datetime.now().date().isoformat()

    conn = get_db_connection()
    history = conn.execute(
        "SELECT module, minutes, date FROM history WHERE user_id = ? ORDER BY id DESC",
        (session["user"],)
    ).fetchall()
    conn.close()

    return render_template("index.html", today=today, history=history)


@app.route("/add", methods=["POST"])
def add_activity():
    if "user" not in session:
        abort(401)

    module = request.form.get("module", "").strip()
    duration_hours = request.form.get("duration_hours")
    duration_minutes = request.form.get("duration_minutes")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    if not module:
        abort(400, "Module name is required")

    total_minutes = 0

    # Duration logic (validated)
    if duration_hours and duration_minutes:
        total_minutes = int(duration_hours) * 60 + int(duration_minutes)

    elif start_time and end_time:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        total_minutes = int((end - start).total_seconds() // 60)

    if total_minutes <= 0:
        abort(400, "Invalid duration")

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO history (user_id, date, module, minutes) VALUES (?, ?, ?, ?)",
        (session["user"], datetime.now().date().isoformat(), module, total_minutes)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/login")
def login():
    # Placeholder auth (clean & explicit)
    session["user"] = "demo_user"
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------- STARTUP --------------------

init_db()

# NOTE:
# Do NOT use app.run() in production.
# Gunicorn will run: gunicorn app:app
