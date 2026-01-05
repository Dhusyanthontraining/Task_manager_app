from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

def get_db_connection():
    conn = sqlite3.connect('tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    today = datetime.now().date().isoformat()
    return render_template('index.html', today=today)

@app.route('/add', methods=['POST'])
def add_activity():
    module = request.form['module']
    duration_hours = request.form.get('duration_hours')
    duration_minutes = request.form.get('duration_minutes')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    # Calculate total duration based on input
    total_minutes = 0
    if duration_hours is not None and duration_minutes is not None:
        total_minutes = int(duration_hours) * 60 + int(duration_minutes)
    elif start_time and end_time:
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        total_minutes = int((end - start).total_seconds() // 60)
    
    # Save to database (for simplicity, assume a 'history' table exists)
    conn = get_db_connection()
    conn.execute('INSERT INTO history (user_id, date, module, minutes) VALUES (?, ?, ?, ?)',
                 (session['user'], datetime.now().date().isoformat(), module, total_minutes))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/login')
def login():
    # Temporary login (no Google yet)
    session['user'] = 'test_user'
    return redirect(url_for('index'))

# Other routes like login, viewing history, etc. would go here

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

