import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "TaskFlow API"
    assert data["status"] == "operational"

def test_tasks_empty():
    """Test tasks endpoint when no tasks exist"""
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["tasks"] == []
