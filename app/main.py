from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(title="TaskFlow API", version="1.0.0")

# In-memory storage
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

@app.get("/")
def root():
    return {"message": "TaskFlow API", "status": "operational"}

@app.get("/health")
def health_check():
    return {"status": "unhealthy", "timestamp": datetime.now().isoformat()}

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
