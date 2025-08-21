from flask import Flask, render_template, request, redirect, session, url_for, flash
import json, os, threading, time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "baby_task_secret"

USERS_FILE = "users.json"
TASKS_FILE = "tasks.json"

# ---------- Helpers ----------
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def reset_daily_tasks():
    """Background job: Reset daily tasks at midnight."""
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:  # At midnight
            tasks = load_json(TASKS_FILE)
            for t in tasks:
                if t["type"] == "daily":
                    t["status"] = "pending"
                    t["done_by"] = None
            save_json(TASKS_FILE, tasks)
            print("✅ Daily tasks reset at midnight")
            time.sleep(60)  # Prevent multiple resets
        time.sleep(30)

# ---------- Auth ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_json(USERS_FILE)
        for user in users:
            if user["username"] == username and user["password"] == password:
                session["user"] = username
                return redirect(url_for("dashboard"))
        flash("Invalid credentials!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    tasks = load_json(TASKS_FILE)
    user = session["user"]

    # Calculate scores
    scores = {}
    for t in tasks:
        if t["status"] == "completed":
            scores[t["done_by"]] = scores.get(t["done_by"], 0) + int(t["points"])

    return render_template("dashboard.html", user=user, tasks=tasks, scores=scores)

# ---------- Tasks ----------
@app.route("/tasks", methods=["GET", "POST"])
def manage_tasks():
    if "user" not in session:
        return redirect(url_for("login"))

    tasks = load_json(TASKS_FILE)
    users = [u["username"] for u in load_json(USERS_FILE)]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            new_task = {
                "id": str(len(tasks) + 1),
                "name": request.form["name"],
                "points": int(request.form["points"]),
                "assigned_to": request.form["assigned_to"],
                "type": request.form["type"],
                "status": "pending",
                "done_by": None
            }
            tasks.append(new_task)
            save_json(TASKS_FILE, tasks)
            flash("Task created successfully!")

        elif action == "update":
            task_id = request.form["id"]
            for t in tasks:
                if t["id"] == task_id:
                    t["status"] = request.form["status"]
                    t["done_by"] = session["user"] if t["status"] == "completed" else None
            save_json(TASKS_FILE, tasks)
            flash("Task updated!")

        elif action == "delete":
            task_id = request.form["id"]
            tasks = [t for t in tasks if t["id"] != task_id]
            save_json(TASKS_FILE, tasks)
            flash("Task deleted!")

    return render_template("tasks.html", tasks=tasks, users=users, user=session["user"])

# ---------- Start Background Reset Thread ----------
threading.Thread(target=reset_daily_tasks, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
