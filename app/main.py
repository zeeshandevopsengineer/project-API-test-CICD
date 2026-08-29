from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import subprocess
import os
import sys

app = FastAPI(title="My 5 Endpoints API", version="1.0.0")

# ============================================
# GLOBAL VARIABLES - FROM ENVIRONMENT
# ============================================
welcome_message = os.environ.get('USER_MESSAGE', 'Welcome to My API!')
welcome_timestamp = datetime.now().isoformat()
selected_color = os.environ.get('USER_COLOR', 'Green')
startup_time = datetime.now()

tasks = []
task_counter = 1

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: str = "medium"

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    created_at: str
    completed: bool = False

# ============================================
# HELPER FUNCTIONS - OS COMMANDS
# ============================================

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def get_os_info():
    return run_command("uname -a")

def get_memory_info():
    output = run_command("free -h")
    lines = output.split('\n')
    if len(lines) > 1:
        mem_line = lines[1].split()
        if len(mem_line) >= 3:
            return {
                "total": mem_line[1] if len(mem_line) > 1 else "N/A",
                "used": mem_line[2] if len(mem_line) > 2 else "N/A",
                "free": mem_line[3] if len(mem_line) > 3 else "N/A",
                "raw": output
            }
    return {"raw": output}

def get_cpu_info():
    return run_command("top -bn1 | grep 'Cpu(s)'")

def get_uptime_seconds():
    output = run_command("cat /proc/uptime")
    try:
        seconds = float(output.split()[0])
        return seconds
    except:
        return 0

def format_uptime(seconds):
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours} hours, {minutes} minutes"
    else:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{days} days, {hours} hours, {minutes} minutes"

# ============================================
# ENDPOINT 1: HEALTH CHECK
# ============================================
@app.get("/health")
def health_check():
    os_info = get_os_info()
    memory = get_memory_info()
    cpu = get_cpu_info()
    uptime_seconds = get_uptime_seconds()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "os": os_info,
            "memory": memory,
            "cpu": cpu,
            "uptime_seconds": uptime_seconds,
            "uptime_human": format_uptime(uptime_seconds)
        }
    }

# ============================================
# ENDPOINT 2: WELCOME MESSAGE
# ============================================
@app.get("/")
def root():
    return {
        "message": welcome_message,
        "timestamp": welcome_timestamp,
        "version": "1.0.0",
        "endpoints": [
            "/health - System health check with OS commands",
            "/ - Welcome message",
            "/learn - Learning options",
            "/time - Colored time display",
            "/web - Full web dashboard"
        ]
    }

# ============================================
# ENDPOINT 3: LEARNING OPTIONS
# ============================================
@app.get("/learn")
def get_learning_options():
    return {
        "options": [
            {"id": 1, "name": "Learn Docker", "message": "Docker Learn with Nana & Zeeshan"},
            {"id": 2, "name": "Learn Git", "message": "GIT Learn with Nana & Zeeshan"},
            {"id": 3, "name": "Learn CICD", "message": "CICD Learn with Nana & Zeeshan"},
            {"id": 4, "name": "Learn Kubernetes", "message": "Kubernets Learn with Nana & Zeeshan"}
        ]
    }

# ============================================
# ENDPOINT 4: COLORED TIME
# ============================================
@app.get("/time")
def get_colored_time():
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "full_datetime": now.isoformat(),
        "color": selected_color,
        "seconds": now.second
    }

# ============================================
# ENDPOINT 5: TASK ENDPOINTS
# ============================================
@app.get("/tasks")
def get_tasks():
    return {"tasks": tasks, "count": len(tasks)}

@app.post("/tasks")
def create_task(task: TaskCreate):
    global task_counter
    new_task = {
        "id": task_counter,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "created_at": datetime.now().isoformat(),
        "completed": False
    }
    tasks.append(new_task)
    task_counter += 1
    return {"task": new_task, "message": "Task created successfully"}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return {"task": task}
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return {"message": "Task completed", "task": task}
    raise HTTPException(status_code=404, detail="Task not found")

# ============================================
# MAIN WEB PAGE
# ============================================
@app.get("/web", response_class=HTMLResponse)
def web_page():
    color = selected_color
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>My 5 Endpoints - Pipeline Run</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            background: #0a192f;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #64ffda;
            text-align: center;
            font-size: 2.5em;
            padding: 20px 0;
        }}
        .subtitle {{
            text-align: center;
            color: #8892b0;
            margin-bottom: 30px;
        }}
        .pipeline-badge {{
            display: inline-block;
            background: #4caf50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card h2 {{
            color: #64ffda;
            font-size: 1.2em;
            margin-bottom: 15px;
        }}
        .card-content {{
            color: #ccd6f6;
            font-size: 0.95em;
            line-height: 1.8;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        .info-item {{
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 8px;
        }}
        .info-item strong {{
            color: #64ffda;
        }}
        .learn-btn {{
            padding: 12px 20px;
            border: 2px solid rgba(100, 255, 218, 0.3);
            border-radius: 10px;
            background: transparent;
            color: #ccd6f6;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1em;
            margin: 5px;
        }}
        .learn-btn:hover {{
            background: rgba(100, 255, 218, 0.1);
            border-color: #64ffda;
        }}
        .learn-btn.selected {{
            background: rgba(100, 255, 218, 0.2);
            border-color: #64ffda;
        }}
        .learn-result {{
            margin-top: 15px;
            padding: 15px;
            background: rgba(100, 255, 218, 0.05);
            border-radius: 10px;
            border-left: 4px solid #64ffda;
            min-height: 50px;
            color: #e6f1ff;
        }}
        .time-display {{
            font-size: 4em;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            font-family: 'Courier New', monospace;
            color: {color};
        }}
        .time-label {{
            text-align: center;
            color: #8892b0;
        }}
        .last-updated {{
            text-align: center;
            color: #8892b0;
            margin-top: 20px;
            padding: 10px;
        }}
        .refresh-btn {{
            display: block;
            margin: 20px auto;
            padding: 10px 30px;
            background: #64ffda;
            color: #0a192f;
            border: none;
            border-radius: 50px;
            font-size: 1em;
            cursor: pointer;
        }}
        .refresh-btn:hover {{
            transform: scale(1.05);
        }}
        .learn-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            .learn-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 My 5 Endpoints</h1>
        <p class="subtitle">
            Pipeline Run: <span class="pipeline-badge">✅ Live Data</span>
        </p>
        
        <div class="grid">
            <div class="card">
                <h2>🖥️ System Health</h2>
                <div class="card-content" id="health-data">
                    Loading...
                </div>
            </div>
            
            <div class="card">
                <h2>📝 Today's Message</h2>
                <div class="card-content" id="welcome-data">
                    Loading...
                </div>
            </div>
            
            <div class="card full-width">
                <h2>📚 Learning Options</h2>
                <div class="card-content">
                    <div class="learn-grid" id="learning-grid">
                        <button class="learn-btn" onclick="selectOption(1)">🐳 Learn Docker</button>
                        <button class="learn-btn" onclick="selectOption(2)">🔀 Learn Git</button>
                        <button class="learn-btn" onclick="selectOption(3)">⚙️ Learn CICD</button>
                        <button class="learn-btn" onclick="selectOption(4)">☸️ Learn Kubernetes</button>
                    </div>
                    <div class="learn-result" id="learn-result">
                        Click an option above to start learning!
                    </div>
                </div>
            </div>
            
            <div class="card full-width">
                <h2>🕐 Live Time</h2>
                <div class="card-content">
                    <div class="time-display" id="time-display">00:00:00</div>
                    <div class="time-label">Color: <span id="color-label" style="color:{color};">{color}</span></div>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="loadAllData()">🔄 Refresh All Data</button>
        <div class="last-updated">
            Last updated: <span id="last-updated">Loading...</span>
        </div>
    </div>

    <script>
        const learningMessages = {{
            1: "🐳 Docker Learn with Nana & Zeeshan",
            2: "🔀 GIT Learn with Nana & Zeeshan",
            3: "⚙️ CICD Learn with Nana & Zeeshan",
            4: "☸️ Kubernets Learn with Nana & Zeeshan"
        }};

        function selectOption(id) {{
            const buttons = document.querySelectorAll('.learn-btn');
            buttons.forEach((btn, index) => {{
                btn.classList.remove('selected');
                if (index + 1 === id) btn.classList.add('selected');
            }});
            document.getElementById('learn-result').innerHTML = 
                '📖 ' + learningMessages[id];
        }}

        async function loadHealth() {{
            try {{
                const res = await fetch('/health');
                const data = await res.json();
                const s = data.system;
                document.getElementById('health-data').innerHTML = `
                    <div class="info-grid">
                        <div class="info-item"><strong>OS:</strong><br>${{s.os || 'N/A'}}</div>
                        <div class="info-item"><strong>Memory:</strong><br>Total: ${{s.memory.total || 'N/A'}}<br>Used: ${{s.memory.used || 'N/A'}}</div>
                        <div class="info-item"><strong>CPU:</strong><br>${{s.cpu || 'N/A'}}</div>
                        <div class="info-item"><strong>Uptime:</strong><br>${{s.uptime_human || 'N/A'}}</div>
                    </div>
                    <div style="font-size:0.8em;color:#8892b0;margin-top:10px;">Updated: ${{new Date(data.timestamp).toLocaleString()}}</div>
                `;
            }} catch(e) {{
                document.getElementById('health-data').innerHTML = '❌ Error loading health data';
            }}
        }}

        async function loadWelcome() {{
            try {{
                const res = await fetch('/');
                const data = await res.json();
                document.getElementById('welcome-data').innerHTML = `
                    <div style="font-size:1.1em;">💬 "${{data.message}}"</div>
                    <div style="font-size:0.85em;color:#8892b0;margin-top:10px;">📅 Entered: ${{new Date(data.timestamp).toLocaleString()}}</div>
                `;
            }} catch(e) {{
                document.getElementById('welcome-data').innerHTML = '❌ Error loading welcome message';
            }}
        }}

        async function loadTime() {{
            try {{
                const res = await fetch('/time');
                const data = await res.json();
                const color = data.color || 'Green';
                document.getElementById('time-display').style.color = color;
                document.getElementById('color-label').textContent = color;
                document.getElementById('color-label').style.color = color;
                document.getElementById('time-display').textContent = data.time;
            }} catch(e) {{
                console.error('Time error:', e);
            }}
        }}

        async function loadAllData() {{
            await loadHealth();
            await loadWelcome();
            await loadTime();
            document.getElementById('last-updated').textContent = new Date().toLocaleString();
        }}

        loadAllData();

        setInterval(() => {{
            const now = new Date();
            document.getElementById('time-display').textContent = now.toTimeString().split(' ')[0];
            document.getElementById('last-updated').textContent = new Date().toLocaleString();
        }}, 1000);

        setInterval(() => {{
            loadHealth();
            loadWelcome();
        }}, 5000);
    </script>
</body>
</html>
    """
    return html

# ============================================
# STARTUP - Print Info
# ============================================
def print_startup_info():
    global welcome_message, welcome_timestamp, selected_color
    
    print("\n" + "="*50)
    print("🚀 My 5 Endpoints API")
    print("="*50)
    print(f"📝 Message: {welcome_message}")
    print(f"🎨 Color: {selected_color}")
    print(f"🌐 Web: http://localhost:8000/web")
    print("="*50 + "\n")

print_startup_info()
