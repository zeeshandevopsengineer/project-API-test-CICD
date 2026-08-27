import pytest
from fastapi.testclient import TestClient
from app.main import app, tasks, task_counter

client = TestClient(app)

def setup_function():
    tasks.clear()
    global task_counter
    task_counter = 1

def test_create_task():
    task_data = {
        "title": "Test Task",
        "description": "This is a test",
        "priority": "high"
    }
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Task created successfully"
    assert data["task"]["title"] == "Test Task"

def test_get_tasks():
    client.post("/tasks", json={"title": "Task 1", "priority": "medium"})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert len(data["tasks"]) == 1

def test_get_single_task():
    create_response = client.post("/tasks", json={"title": "Task 1"})
    task_id = create_response.json()["task"]["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task"]["id"] == task_id

def test_complete_task():
    create_response = client.post("/tasks", json={"title": "Task to complete"})
    task_id = create_response.json()["task"]["id"]
    response = client.put(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["message"] == "Task completed"
    assert response.json()["task"]["completed"] == True

def test_nonexistent_task():
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
