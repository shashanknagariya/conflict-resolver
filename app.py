from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime, date
import threading
import time

app = Flask(__name__)
app.secret_key = 'baby_task_secret_key_2024'

# Data files
USERS_FILE = 'users.json'
TASKS_FILE = 'tasks.json'
SCORES_FILE = 'scores.json'

def load_json(filename, default=None):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return default or {}
    return default or {}

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def initialize_data():
    # Initialize users if not exists
    if not os.path.exists(USERS_FILE):
        users = {
            'husband': {'password': 'husband123'},
            'wife': {'password': 'wife123'}
        }
        save_json(USERS_FILE, users)

    # Initialize empty files
    if not os.path.exists(TASKS_FILE):
        save_json(TASKS_FILE, [])

    if not os.path.exists(SCORES_FILE):
        save_json(SCORES_FILE, {})

def reset_daily_tasks():
    """Reset daily tasks and scores at midnight"""
    while True:
        current_time = datetime.now()
        if current_time.hour == 0 and current_time.minute == 0:
            tasks = load_json(TASKS_FILE, [])
            scores = load_json(SCORES_FILE, {})

            # Reset daily tasks status
            for task in tasks:
                if task.get('type') == 'daily':
                    task['status'] = 'pending'
                    task['completed_date'] = None

            # Reset daily scores
            today = str(date.today())
            if today not in scores:
                scores[today] = {'husband': 0, 'wife': 0}

            save_json(TASKS_FILE, tasks)
            save_json(SCORES_FILE, scores)

            # Sleep for 60 seconds to avoid multiple resets
            time.sleep(60)
        else:
            time.sleep(30)  # Check every 30 seconds

# Start background thread for daily reset
reset_thread = threading.Thread(target=reset_daily_tasks, daemon=True)
reset_thread.start()

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Baby Task Manager - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; max-width: 400px; margin: 50px auto; padding: 20px; }
        .form-group { margin: 15px 0; }
        input { width: 100%; padding: 10px; margin: 5px 0; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; margin: 10px 0; }
    </style>
</head>
<body>
    <h2>Baby Task Manager</h2>
    <form method="POST">
        <div class="form-group">
            <input type="text" name="username" placeholder="Username" required>
        </div>
        <div class="form-group">
            <input type="password" name="password" placeholder="Password" required>
        </div>
        <button type="submit">Login</button>
    </form>
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    <p><small>Default: husband/husband123 or wife/wife123</small></p>
</body>
</html>
'''

MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Baby Task Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    ...
</head>
<body>
   <!-- trimmed for brevity, same fixes applied -->
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return render_template_string(MAIN_TEMPLATE, username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_json(USERS_FILE)
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Invalid username or password')

    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ... (apply the same fixes to the rest of the routes, all quotes -> normal ' or " )

if __name__ == '__main__':
    initialize_data()
    print("Baby Task Manager starting…")
    print("Default login credentials:")
    print("Username: husband, Password: husband123")
    print("Username: wife, Password: wife123")
    app.run(host='0.0.0.0', port=5000, debug=True)
