import pytest
from fastapi.testclient import TestClient
from app.main import app, tasks, task_counter

client = TestClient(app)

def setup_function():
    """Reset the tasks before each test"""
    tasks.clear()
    global task_counter
    task_counter = 1

def test_create_task():
    """Test creating a new task"""
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
    assert data["task"]["priority"] == "high"
    assert "id" in data["task"]

def test_get_tasks():
    """Test retrieving all tasks"""
    # Create a task first
    client.post("/tasks", json={"title": "Task 1", "priority": "medium"})
    
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert len(data["tasks"]) == 1

def test_get_single_task():
    """Test retrieving a single task"""
    # Create a task
    create_response = client.post("/tasks", json={"title": "Task 1"})
    task_id = create_response.json()["task"]["id"]
    
    # Get the task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task"]["id"] == task_id
    assert data["task"]["title"] == "Task 1"

def test_complete_task():
    """Test completing a task"""
    # Create a task
    create_response = client.post("/tasks", json={"title": "Task to complete"})
    task_id = create_response.json()["task"]["id"]
    
    # Complete the task
    response = client.put(f"/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["message"] == "Task completed"
    assert response.json()["task"]["completed"] == True

def test_nonexistent_task():
    """Test retrieving a non-existent task"""
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
