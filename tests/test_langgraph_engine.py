import json
import pytest
from pathlib import Path
from backend.agent.interview_graph import interview_agent_graph, InterviewGraphState
from backend.services.session_manager import session_manager
from backend.services.interview_manager import interview_manager

@pytest.fixture(autouse=True)
def reset_sessions():
    session_manager.clear_all()

def load_sample_candidate():
    candidates_path = Path(__file__).resolve().parent.parent / "candidates.json"
    with open(candidates_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["candidates"][0] # Sarah Johnson

def test_langgraph_compile_and_initial_run():
    cand_data = load_sample_candidate()
    initial_state: InterviewGraphState = {
        "session_id": "test-lg-001",
        "candidate_raw": cand_data,
        "question_count": 0,
        "covered_days": [],
        "history": [],
        "strengths": [],
        "gaps": [],
        "done": False
    }

    result = interview_agent_graph.invoke(initial_state)

    assert result["done"] is False
    assert "reply" in result
    assert len(result["reply"]) > 10
    assert len(result["covered_days"]) == 1
    assert result["question_count"] == 1

def test_langgraph_full_interview_manager():
    session_id = "test-lg-manager-001"
    cand_data = load_sample_candidate()

    reply, done, feedback = interview_manager.start_interview(session_id, cand_data)
    assert done is False
    assert len(reply) > 10

    answers = [
        "Chunking strategy depends on text structure; overlapping chunks preserve cross-boundary semantics.",
        "Vector databases like ChromaDB use HNSW indexing to minimize query latency for similarity lookups.",
        "Hybrid retrieval routes queries between SQLite for structured criteria and ChromaDB for semantic search.",
        "System prompts enforce strict grounding, requiring model to admit uncertainty when context lacks answers.",
        "FastAPI session management relies on stateless bearer tokens and standard context passing.",
        "Multi-agent orchestrators delegate domain tasks to specialist agents via ReAct loops and tool calls.",
        "Model Context Protocol (MCP) standardizes JSON-RPC schemas so external clients execute tools safely.",
        "Kubernetes deployment involves multi-stage Docker builds, mounting secrets, and setting health probes."
    ]

    for idx, ans in enumerate(answers):
        reply, done, feedback = interview_manager.continue_interview(session_id, ans)
        if idx < 7:
            assert done is False
        else:
            assert done is True
            assert feedback is not None
            assert "summary" in feedback
            assert len(feedback["strengths"]) > 0
            assert len(feedback["gaps"]) > 0
            assert len(feedback["next"]) > 0
