import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.session_manager import session_manager

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_sessions():
    session_manager.clear_all()

def load_sample_candidate(candidate_id: str = "CAND-001"):
    candidates_path = Path(__file__).resolve().parent.parent / "candidates.json"
    with open(candidates_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for c in data.get("candidates", []):
        if c["member"]["id"] == candidate_id:
            return c
    return data["candidates"][0]

def test_full_interview_lifecycle():
    session_id = "test-full-sim-001"
    cand_data = load_sample_candidate("CAND-001") # Sarah Johnson (Senior)

    # 1. Start Interview
    res = client.post("/api/interview", json={"sessionId": session_id, "candidate": cand_data})
    assert res.status_code == 200
    data = res.json()
    assert data["done"] is False
    assert len(data["reply"]) > 10

    # 2. Simulate 8 candidate answer turns
    candidate_answers = [
        "In RAG pipelines, text chunking dictates embedding granularity. I use overlap to preserve semantic context across chunk boundaries.",
        "Vector database indexing using HNSW optimizes query performance at the cost of RAM, which is ideal for sub-50ms retrieval SLA.",
        "I combine SQLite for structured policy lookups and ChromaDB vector search using a router component that merges results.",
        "System prompts must enforce strict guardrails, instructs LLMs to say 'I don't know' if context is missing, and restrict response formats.",
        "FastAPI session management relies on async handlers and redis or in-memory state tracking with standard Bearer token header propagation.",
        "Multi-agent orchestrators use a central router or supervisor agent to delegate sub-tasks to domain specialist agents via structured tool calls.",
        "Model Context Protocol (MCP) defines standardized JSON-RPC protocols so tools can be exposed cleanly to any MCP-compatible AI client.",
        "Kubernetes deployment involves Docker multi-stage builds, mounting secrets via k8s secrets, and configuring readiness probes on /health."
    ]

    for idx, answer in enumerate(candidate_answers):
        res = client.post("/api/interview", json={"sessionId": session_id, "message": answer})
        assert res.status_code == 200
        data = res.json()
        
        # Check turn state
        if idx < 7: # Turns 1 to 7 should not end
            assert data["done"] is False
        else: # Turn 8 should conclude interview
            assert data["done"] is True
            assert "feedback" in data
            feedback = data["feedback"]
            assert "summary" in feedback
            assert len(feedback["strengths"]) > 0
            assert len(feedback["gaps"]) > 0
            assert len(feedback["next"]) > 0

    # Verify session internal state in session_manager
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session.question_count >= 8
    assert len(set(session.covered_days)) >= 4
    assert session.done is True
