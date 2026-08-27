import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "system" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "timestamp" in data

def test_learn_endpoint():
    response = client.get("/learn")
    assert response.status_code == 200
    data = response.json()
    assert "options" in data
    assert len(data["options"]) == 4

def test_time_endpoint():
    response = client.get("/time")
    assert response.status_code == 200
    data = response.json()
    assert "time" in data
    assert "color" in data

def test_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
