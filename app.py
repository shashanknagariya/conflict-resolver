from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json, os, threading, time
from datetime import datetime, date

# Look for templates in root (no folders)
app = Flask(__name__, template_folder='.')
app.secret_key = os.environ.get("SECRET_KEY", "baby_task_secret_key_2024")

USERS_FILE = "users.json"
TASKS_FILE = "tasks.json"

# ------------- Utils & Data Access -------------

def log(msg):
    app.logger.info(msg)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        log(f"Error loading {path}: {e}")
        return default

def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        log(f"Error saving {path}: {e}")

def initialize_data():
    # users
    if not os.path.exists(USERS_FILE):
        users = [
            {"username": "husband", "password": "husband123"},
            {"username": "wife", "password": "wife123"}
        ]
        save_json(USERS_FILE, users)
        log("Created users.json with default users")
    # tasks
    if not os.path.exists(TASKS_FILE):
        save_json(TASKS_FILE, [])
        log("Created empty tasks.json")

def today_str():
    return str(date.today())

def next_task_id(tasks):
    mx = 0
    for t in tasks:
        try:
            mx = max(mx, int(t.get("id", 0)))
        except:
            pass
    return mx + 1

# ------------- Midnight Reset Thread -------------

def reset_daily_tasks():
    """Reset all DAILY tasks to pending at midnight (local time)."""
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            tasks = load_json(TASKS_FILE, [])
            for t in tasks:
                if t.get("type") == "daily":
                    t["status"] = "pending"
                    t["completed_date"] = None
                    t["done_by"] = None
            save_json(TASKS_FILE, tasks)
            log("✅ Daily tasks reset at midnight")
            time.sleep(60)  # avoid multiple triggers
        time.sleep(30)

# Start background reset
threading.Thread(target=reset_daily_tasks, daemon=True).start()

# ------------- Auth -------------

@app.route("/", methods=["GET", "POST"])
def login():
    log(f"Login route hit, method={request.method}")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        users = load_json(USERS_FILE, [])
        ok = any(u["username"] == username and u["password"] == password for u in users)
        if ok:
            session["username"] = username
            log(f"Login success for {username}")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.")
        log(f"Login failed for {username}")
    return render_template("login.html")

@app.route("/logout")
def logout():
    user = session.pop("username", None)
    log(f"Logout: {user}")
    return redirect(url_for("login"))

# ------------- Pages -------------

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    tasks = load_json(TASKS_FILE, [])
    user = session["username"]
    today = today_str()

    # Today’s scores
    scores = {"husband": 0, "wife": 0}
    for t in tasks:
        if t.get("status") == "completed" and t.get("completed_date") == today:
            db = t.get("done_by")
            if db in scores:
                try:
                    scores[db] += int(t.get("points", 0))
                except:
                    pass

    # Summary counts
    pending = sum(1 for t in tasks if t.get("status") == "pending")
    completed_today = sum(1 for t in tasks if t.get("status") == "completed" and t.get("completed_date") == today)
    unassigned = sum(1 for t in tasks if t.get("assigned_to") == "unassigned")

    return render_template(
        "dashboard.html",
        user=user,
        scores=scores,
        pending=pending,
        completed_today=completed_today,
        unassigned=unassigned,
        tasks=tasks,
        today=today
    )

@app.route("/tasks")
def manage_tasks():
    if "username" not in session:
        return redirect(url_for("login"))
    tasks = load_json(TASKS_FILE, [])
    users = [u["username"] for u in load_json(USERS_FILE, [])] + ["unassigned"]
    return render_template("tasks.html", tasks=tasks, users=users, user=session["username"])

# ------------- JSON APIs (used by JS) -------------

@app.route("/api/task/create", methods=["POST"])
def api_task_create():
    if "username" not in session:
        return jsonify(success=False, error="Unauthorized"), 401
    data = request.get_json(force=True)
    tasks = load_json(TASKS_FILE, [])
    new_task = {
        "id": next_task_id(tasks),
        "name": data.get("name", "").strip(),
        "points": int(data.get("points", 1)),
        "assigned_to": data.get("assigned_to", "unassigned"),
        "type": data.get("type", "daily"),
        "status": "pending",
        "created_date": today_str(),
        "completed_date": None,
        "done_by": None
    }
    tasks.append(new_task)
    save_json(TASKS_FILE, tasks)
    log(f"Task created by {session['username']}: {new_task}")
    return jsonify(success=True, task=new_task)

@app.route("/api/task/status", methods=["POST"])
def api_task_status():
    if "username" not in session:
        return jsonify(success=False, error="Unauthorized"), 401
    data = request.get_json(force=True)
    task_id = int(data.get("task_id"))
    completed = bool(data.get("completed"))
    tasks = load_json(TASKS_FILE, [])
    updated = False
    for t in tasks:
        if int(t.get("id")) == task_id:
            if completed:
                t["status"] = "completed"
                t["completed_date"] = today_str()
                t["done_by"] = session["username"]
            else:
                t["status"] = "pending"
                t["completed_date"] = None
                t["done_by"] = None
            updated = True
            break
    if updated:
        save_json(TASKS_FILE, tasks)
        log(f"Task {task_id} status set to {'completed' if completed else 'pending'} by {session['username']}")
        return jsonify(success=True)
    return jsonify(success=False, error="Task not found"), 404

@app.route("/api/task/delete", methods=["POST"])
def api_task_delete():
    if "username" not in session:
        return jsonify(success=False, error="Unauthorized"), 401
    data = request.get_json(force=True)
    task_id = int(data.get("task_id"))
    tasks = load_json(TASKS_FILE, [])
    new_tasks = [t for t in tasks if int(t.get("id")) != task_id]
    if len(new_tasks) == len(tasks):
        return jsonify(success=False, error="Task not found"), 404
    save_json(TASKS_FILE, new_tasks)
    log(f"Task {task_id} deleted by {session['username']}")
    return jsonify(success=True)

@app.route("/api/task/forward", methods=["POST"])
def api_task_forward():
    if "username" not in session:
        return jsonify(success=False, error="Unauthorized"), 401
    data = request.get_json(force=True)
    task_id = int(data.get("task_id"))
    new_assignee = data.get("new_assignee", "unassigned")
    tasks = load_json(TASKS_FILE, [])
    updated = False
    for t in tasks:
        if int(t.get("id")) == task_id:
            t["assigned_to"] = new_assignee
            updated = True
            break
    if updated:
        save_json(TASKS_FILE, tasks)
        log(f"Task {task_id} forwarded to {new_assignee} by {session['username']}")
        return jsonify(success=True)
    return jsonify(success=False, error="Task not found"), 404

# ------------- Main -------------

if __name__ == "__main__":
    initialize_data()
    port = int(os.environ.get("PORT", 5000))  # Render/Heroku will set PORT
    log("Baby Task Manager starting…")
    app.run(host="0.0.0.0", port=port, debug=True)
