import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------- APP CONFIG --------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_fallback_key")

DATABASE = "tracker.db"


# -------------------- DB UTILITIES --------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------- ROUTES --------------------

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    today = datetime.now().date().isoformat()

    conn = get_db_connection()
    history = conn.execute(
        """
        SELECT module, minutes, date
        FROM history
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("index.html", today=today, history=history)


@app.route("/add", methods=["POST"])
def add_activity():
    if "user_id" not in session:
        abort(401)

    module = request.form.get("module", "").strip()
    duration_minutes = request.form.get("duration_minutes")

    if not module or not duration_minutes:
        abort(400, "Invalid input")

    total_minutes = int(duration_minutes)

    if total_minutes <= 0:
        abort(400, "Invalid duration")

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO history (user_id, date, module, minutes)
        VALUES (?, ?, ?, ?)
        """,
        (session["user_id"], datetime.now().date().isoformat(), module, total_minutes)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# -------------------- AUTH --------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not email or not password:
            return "Email and password required", 400

        if password != confirm_password:
            return "Passwords do not match", 400

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (?, ?, ?)
                """,
                (email, password_hash, datetime.utcnow().isoformat())
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered", 400

        user = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        session["user_id"] = user["id"]
        return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return "Invalid email or password", 400

        session["user_id"] = user["id"]
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
