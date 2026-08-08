import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.session_manager import session_manager

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_sessions():
    session_manager.clear_all()

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "AI Technical Interview Agent"}

def test_start_interview():
    payload = {
        "sessionId": "test-session-101",
        "candidate": {
            "member": {
                "id": "CAND-001",
                "name": "Sarah Johnson",
                "jobRole": "Senior Data Engineer",
                "yearsExperience": 9
            }
        }
    }
    response = client.post("/api/interview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["done"] is False
    assert data.get("feedback") is None

def test_continue_interview():
    # 1. Start session
    start_payload = {
        "sessionId": "test-session-102",
        "candidate": {"member": {"name": "Test Candidate"}}
    }
    client.post("/api/interview", json=start_payload)

    # 2. Send answer turn
    turn_payload = {
        "sessionId": "test-session-102",
        "message": "I have experience with vector databases and RAG pipelines."
    }
    response = client.post("/api/interview", json=turn_payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["done"] is False

def test_continue_nonexistent_session():
    payload = {
        "sessionId": "nonexistent-session",
        "message": "Hello?"
    }
    response = client.post("/api/interview", json=payload)
    assert response.status_code == 404
