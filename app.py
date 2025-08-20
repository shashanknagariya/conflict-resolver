from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime, date
import threading
import time

app = Flask(**name**)
app.secret_key = ‘baby_task_secret_key_2024’

# Data files

USERS_FILE = ‘users.json’
TASKS_FILE = ‘tasks.json’
SCORES_FILE = ‘scores.json’

def load_json(filename, default=None):
if os.path.exists(filename):
try:
with open(filename, ‘r’) as f:
return json.load(f)
except:
return default or {}
return default or {}

def save_json(filename, data):
with open(filename, ‘w’) as f:
json.dump(data, f, indent=2, default=str)

def initialize_data():
# Initialize users if not exists
if not os.path.exists(USERS_FILE):
users = {
‘husband’: {‘password’: ‘husband123’},
‘wife’: {‘password’: ‘wife123’}
}
save_json(USERS_FILE, users)

```
# Initialize empty files
if not os.path.exists(TASKS_FILE):
    save_json(TASKS_FILE, [])

if not os.path.exists(SCORES_FILE):
    save_json(SCORES_FILE, {})
```

def reset_daily_tasks():
“”“Reset daily tasks and scores at midnight”””
while True:
current_time = datetime.now()
if current_time.hour == 0 and current_time.minute == 0:
tasks = load_json(TASKS_FILE, [])
scores = load_json(SCORES_FILE, {})

```
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
```

# Start background thread for daily reset

reset_thread = threading.Thread(target=reset_daily_tasks, daemon=True)
reset_thread.start()

# HTML Templates

LOGIN_TEMPLATE = ‘’’

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

MAIN_TEMPLATE = ‘’’

<!DOCTYPE html>

<html>
<head>
    <title>Baby Task Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#007bff">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Baby Tasks">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23007bff'/><text y='70' font-size='60' text-anchor='middle' x='50' fill='white'>👶</text></svg>">
    <style>
        body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .nav { margin: 20px 0; }
        .nav button { margin: 5px; padding: 10px 15px; cursor: pointer; }
        .nav button.active { background: #007bff; color: white; }
        .section { display: none; }
        .section.active { display: block; }
        .task-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .task-item.completed { background: #d4edda; }
        .task-item.pending { background: #fff3cd; }
        input, select, button { padding: 8px; margin: 5px; }
        .points { font-weight: bold; color: #007bff; }
        .score-card { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .task-actions button { padding: 5px 10px; margin: 2px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Baby Task Manager</h2>
        <div>
            <span>Welcome, {{ username }}!</span>
            <a href="/logout" style="margin-left: 15px;">Logout</a>
        </div>
    </div>

```
<div class="nav">
    <button onclick="showSection('dashboard')" class="nav-btn active">Dashboard</button>
    <button onclick="showSection('create-task')" class="nav-btn">Create Task</button>
    <button onclick="showSection('my-tasks')" class="nav-btn">My Tasks</button>
    <button onclick="showSection('all-tasks')" class="nav-btn">All Tasks</button>
</div>

<!-- Dashboard Section -->
<div id="dashboard" class="section active">
    <h3>Today's Summary</h3>
    <div id="score-summary"></div>
    <div id="task-summary"></div>
</div>

<!-- Create Task Section -->
<div id="create-task" class="section">
    <h3>Create New Task</h3>
    <form id="task-form">
        <div>
            <input type="text" id="task-name" placeholder="Task Name" required>
        </div>
        <div>
            <select id="task-points">
                <option value="">Select Points</option>
                <option value="1">1 - Very Easy</option>
                <option value="2">2 - Easy</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5 - Medium</option>
                <option value="6">6</option>
                <option value="7">7</option>
                <option value="8">8 - Hard</option>
                <option value="9">9</option>
                <option value="10">10 - Very Hard</option>
            </select>
        </div>
        <div>
            <select id="task-assigned">
                <option value="husband">Husband</option>
                <option value="wife">Wife</option>
                <option value="unassigned">Unassigned</option>
            </select>
        </div>
        <div>
            <select id="task-type">
                <option value="daily">Daily Task</option>
                <option value="onetime">One-time Task</option>
            </select>
        </div>
        <button type="submit">Create Task</button>
    </form>
</div>

<!-- My Tasks Section -->
<div id="my-tasks" class="section">
    <h3>My Tasks</h3>
    <div id="my-tasks-list"></div>
</div>

<!-- All Tasks Section -->
<div id="all-tasks" class="section">
    <h3>All Tasks</h3>
    <div id="all-tasks-list"></div>
</div>

<script>
    let currentUser = '{{ username }}';
    
    function showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        
        // Show selected section
        document.getElementById(sectionId).classList.add('active');
        event.target.classList.add('active');
        
        // Load data for the section
        if (sectionId === 'dashboard') loadDashboard();
        if (sectionId === 'my-tasks') loadMyTasks();
        if (sectionId === 'all-tasks') loadAllTasks();
    }

    function loadDashboard() {
        fetch('/api/dashboard')
            .then(response => response.json())
            .then(data => {
                document.getElementById('score-summary').innerHTML = `
                    <div class="score-card">
                        <h4>Today's Scores</h4>
                        <p>Husband: <span class="points">${data.scores.husband}</span> points</p>
                        <p>Wife: <span class="points">${data.scores.wife}</span> points</p>
                    </div>
                `;
                
                document.getElementById('task-summary').innerHTML = `
                    <div class="score-card">
                        <h4>Task Summary</h4>
                        <p>Pending Tasks: ${data.task_summary.pending}</p>
                        <p>Completed Today: ${data.task_summary.completed}</p>
                        <p>Unassigned Tasks: ${data.task_summary.unassigned}</p>
                    </div>
                `;
            });
    }

    function loadMyTasks() {
        fetch('/api/my-tasks')
            .then(response => response.json())
            .then(data => {
                let html = '';
                data.tasks.forEach(task => {
                    html += createTaskHTML(task);
                });
                document.getElementById('my-tasks-list').innerHTML = html || '<p>No tasks assigned to you.</p>';
            });
    }

    function loadAllTasks() {
        fetch('/api/all-tasks')
            .then(response => response.json())
            .then(data => {
                let html = '';
                data.tasks.forEach(task => {
                    html += createTaskHTML(task);
                });
                document.getElementById('all-tasks-list').innerHTML = html || '<p>No tasks found.</p>';
            });
    }

    function createTaskHTML(task) {
        let statusClass = task.status === 'completed' ? 'completed' : 'pending';
        let statusText = task.status === 'completed' ? 'Completed' : 'Pending';
        
        return `
            <div class="task-item ${statusClass}">
                <h4>${task.name}</h4>
                <p>Points: <span class="points">${task.points}</span> | 
                   Assigned to: ${task.assigned_to} | 
                   Type: ${task.type} | 
                   Status: ${statusText}</p>
                <div class="task-actions">
                    ${task.status === 'pending' ? `<button onclick="completeTask(${task.id})">Complete</button>` : ''}
                    <button onclick="editTask(${task.id})">Edit</button>
                    <button onclick="deleteTask(${task.id})">Delete</button>
                    <button onclick="forwardTask(${task.id})">Forward</button>
                </div>
            </div>
        `;
    }

    function completeTask(taskId) {
        fetch('/api/complete-task', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({task_id: taskId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadMyTasks();
                loadAllTasks();
                loadDashboard();
            }
        });
    }

    function editTask(taskId) {
        let newName = prompt('Enter new task name:');
        let newPoints = prompt('Enter new points (1-10):');
        if (newName && newPoints) {
            fetch('/api/edit-task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    task_id: taskId,
                    name: newName,
                    points: parseInt(newPoints)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadMyTasks();
                    loadAllTasks();
                }
            });
        }
    }

    function deleteTask(taskId) {
        if (confirm('Are you sure you want to delete this task?')) {
            fetch('/api/delete-task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: taskId})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadMyTasks();
                    loadAllTasks();
                    loadDashboard();
                }
            });
        }
    }

    function forwardTask(taskId) {
        let newAssignee = prompt('Forward to (husband/wife/unassigned):');
        if (newAssignee && ['husband', 'wife', 'unassigned'].includes(newAssignee)) {
            fetch('/api/forward-task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    task_id: taskId,
                    new_assignee: newAssignee
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadMyTasks();
                    loadAllTasks();
                    loadDashboard();
                }
            });
        }
    }

    // Create task form submission
    document.getElementById('task-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        let formData = {
            name: document.getElementById('task-name').value,
            points: parseInt(document.getElementById('task-points').value),
            assigned_to: document.getElementById('task-assigned').value,
            type: document.getElementById('task-type').value
        };

        fetch('/api/create-task', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('task-form').reset();
                alert('Task created successfully!');
                loadDashboard();
            }
        });
    });

    // Load dashboard on page load
    loadDashboard();

    // PWA Service Worker Registration
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('SW registered: ', registration);
                })
                .catch(function(registrationError) {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
</script>
```

</body>
</html>
'''

# Routes

@app.route(’/’)
def index():
if ‘username’ in session:
return render_template_string(MAIN_TEMPLATE, username=session[‘username’])
return redirect(url_for(‘login’))

@app.route(’/login’, methods=[‘GET’, ‘POST’])
def login():
if request.method == ‘POST’:
username = request.form[‘username’]
password = request.form[‘password’]

```
    users = load_json(USERS_FILE)
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('index'))
    else:
        return render_template_string(LOGIN_TEMPLATE, error='Invalid username or password')

return render_template_string(LOGIN_TEMPLATE)
```

@app.route(’/logout’)
def logout():
session.pop(‘username’, None)
return redirect(url_for(‘login’))

@app.route(’/api/dashboard’)
def api_dashboard():
today = str(date.today())
scores = load_json(SCORES_FILE, {})
tasks = load_json(TASKS_FILE, [])

```
today_scores = scores.get(today, {'husband': 0, 'wife': 0})

pending_tasks = len([t for t in tasks if t['status'] == 'pending'])
completed_tasks = len([t for t in tasks if t['status'] == 'completed' and t.get('completed_date') == today])
unassigned_tasks = len([t for t in tasks if t['assigned_to'] == 'unassigned'])

return jsonify({
    'scores': today_scores,
    'task_summary': {
        'pending': pending_tasks,
        'completed': completed_tasks,
        'unassigned': unassigned_tasks
    }
})
```

@app.route(’/api/my-tasks’)
def api_my_tasks():
tasks = load_json(TASKS_FILE, [])
username = session.get(‘username’)
my_tasks = [t for t in tasks if t[‘assigned_to’] == username]
return jsonify({‘tasks’: my_tasks})

@app.route(’/api/all-tasks’)
def api_all_tasks():
tasks = load_json(TASKS_FILE, [])
return jsonify({‘tasks’: tasks})

@app.route(’/api/create-task’, methods=[‘POST’])
def api_create_task():
data = request.json
tasks = load_json(TASKS_FILE, [])

```
# Generate new task ID
max_id = max([t.get('id', 0) for t in tasks], default=0)

new_task = {
    'id': max_id + 1,
    'name': data['name'],
    'points': data['points'],
    'assigned_to': data['assigned_to'],
    'type': data['type'],
    'status': 'pending',
    'created_date': str(date.today()),
    'completed_date': None
}

tasks.append(new_task)
save_json(TASKS_FILE, tasks)

return jsonify({'success': True})
```

@app.route(’/api/complete-task’, methods=[‘POST’])
def api_complete_task():
data = request.json
tasks = load_json(TASKS_FILE, [])
scores = load_json(SCORES_FILE, {})
today = str(date.today())
username = session.get(‘username’)

```
# Find and update task
for task in tasks:
    if task['id'] == data['task_id']:
        task['status'] = 'completed'
        task['completed_date'] = today
        
        # Update scores
        if today not in scores:
            scores[today] = {'husband': 0, 'wife': 0}
        
        if username in scores[today]:
            scores[today][username] += task['points']
        
        break

save_json(TASKS_FILE, tasks)
save_json(SCORES_FILE, scores)

return jsonify({'success': True})
```

@app.route(’/api/edit-task’, methods=[‘POST’])
def api_edit_task():
data = request.json
tasks = load_json(TASKS_FILE, [])

```
for task in tasks:
    if task['id'] == data['task_id']:
        task['name'] = data['name']
        task['points'] = data['points']
        break

save_json(TASKS_FILE, tasks)
return jsonify({'success': True})
```

@app.route(’/api/delete-task’, methods=[‘POST’])
def api_delete_task():
data = request.json
tasks = load_json(TASKS_FILE, [])

```
tasks = [t for t in tasks if t['id'] != data['task_id']]
save_json(TASKS_FILE, tasks)

return jsonify({'success': True})
```

@app.route(’/manifest.json’)
def manifest():
return jsonify({
“name”: “Baby Task Manager”,
“short_name”: “BabyTasks”,
“description”: “Simple task manager for parents”,
“start_url”: “/”,
“display”: “standalone”,
“background_color”: “#ffffff”,
“theme_color”: “#007bff”,
“icons”: [
{
“src”: “data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'><rect width='192' height='192' fill='%23007bff'/><text y='130' font-size='100' text-anchor='middle' x='96' fill='white'>👶</text></svg>”,
“sizes”: “192x192”,
“type”: “image/svg+xml”
},
{
“src”: “data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect width='512' height='512' fill='%23007bff'/><text y='350' font-size='300' text-anchor='middle' x='256' fill='white'>👶</text></svg>”,
“sizes”: “512x512”,
“type”: “image/svg+xml”
}
]
})

@app.route(’/sw.js’)
def service_worker():
return ‘’’
const CACHE_NAME = ‘baby-task-manager-v1’;
const urlsToCache = [
‘/’,
‘/manifest.json’
];

self.addEventListener(‘install’, function(event) {
event.waitUntil(
caches.open(CACHE_NAME)
.then(function(cache) {
return cache.addAll(urlsToCache);
})
);
});

self.addEventListener(‘fetch’, function(event) {
event.respondWith(
caches.match(event.request)
.then(function(response) {
if (response) {
return response;
}
return fetch(event.request);
}
)
);
});
‘’’, 200, {‘Content-Type’: ‘application/javascript’}

@app.route(’/api/forward-task’, methods=[‘POST’])
def api_forward_task():
data = request.json
tasks = load_json(TASKS_FILE, [])

```
for task in tasks:
    if task['id'] == data['task_id']:
        task['assigned_to'] = data['new_assignee']
        break

save_json(TASKS_FILE, tasks)
return jsonify({'success': True})
```

if **name** == ‘**main**’:
initialize_data()
print(“Baby Task Manager starting…”)
print(“Default login credentials:”)
print(“Username: husband, Password: husband123”)
print(“Username: wife, Password: wife123”)
app.run(host=‘0.0.0.0’, port=5000, debug=True)
