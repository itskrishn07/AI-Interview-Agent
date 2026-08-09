# AI Technical Interview Agent — ABTalks Hackathon

An adaptive, realistic, multi-turn AI Technical Interviewer powered by **LangGraph**, **FastAPI**, **Mistral AI**, and a modern **React SPA Frontend**.

Built for the **ABTalks Hackathon** ("Build the interviewer, not the interview").

---

## 🔗 Live Deployments

- 🌐 **Frontend App (Vercel)**: [https://ai-interview-agent-lime.vercel.app](https://ai-interview-agent-lime.vercel.app)
- ⚙️ **Backend API (Render)**: [https://ai-interview-agent-70qf.onrender.com](https://ai-interview-agent-70qf.onrender.com)
- 📖 **Interactive API Docs (Swagger)**: [https://ai-interview-agent-70qf.onrender.com/docs](https://ai-interview-agent-70qf.onrender.com/docs)
- 📝 **Vibe-Coding Prompts Documentation**: [`prompts.md`](prompts.md)

---

## 🌟 Key Features

- **LangGraph Agent Orchestration**: Formalized StateGraph workflow routing turns through Candidate Analysis, Answer Evaluation, Completion Router, Topic Selection, Adaptive Question Generation, and Feedback Synthesis.
- **Candidate Intelligence**: Parses candidate profiles from `candidates.json`, analyzing experience level, completed missions, first-try successes, skipped topics, and attempt history to extract learning signals.
- **Adaptive Interview Loop**: Dynamic follow-up routing (`DEEPER_FOLLOWUP`, `CLARIFICATION`, `FOUNDATIONAL`, `NEW_TOPIC`, `SCENARIO_TRADEOFF`) tailored to response quality and seniority level.
- **Deterministic Curriculum Grounding**: Selectively retrieves objectives and tools from `curriculum.json` (31-day AI Cohort curriculum) without context overloading.
- **Hard Constraints Enforcement**: Enforces `minimum_questions >= 8` AND `minimum_curriculum_days >= 4` in application router logic before an interview can conclude (`done = true`).
- **Evidence-Based Feedback**: Generates structured, actionable feedback (`summary`, `strengths`, `gaps`, `next`) upon interview completion.
- **Strict API Specification Compliance**: Exposes `POST /api/interview` matching [`technical-spec.md`](technical-spec.md).
- **Dual UI Support**:
  - **Modern React SPA (`frontend/src/`)**: High-contrast cyber-teal dark mode UI featuring 20 candidate selector cards, real-time chat workspace with auto-scroll, live question progress bar, and feedback dashboard.
  - **Streamlit UI (`frontend/app.py`)**: Lightweight alternative Python Streamlit dashboard.

---

## 📐 LangGraph Agent Architecture Overview

```text
                                 REACT FRONTEND UI (Vite)
                           https://ai-interview-agent-lime.vercel.app
                                             |
                                             v
                                FASTAPI BACKEND SERVER (Render)
                                             |
                                             v
                                 POST /api/interview ENDPOINT
                                             |
                                             v
                                   LANGGRAPH STATE GRAPH
                              (backend/agent/interview_graph.py)
                                             |
              +------------------------------+------------------------------+
              |                              |                              |
              v                              v                              v
      Candidate Analyzer           Curriculum Retriever           Session Manager
     (Learning Signals)           (Deterministic Lookup)        (InterviewGraphState)
              |                              |                              |
              +------------------------------+------------------------------+
                                             |
                                             v
                                  ADAPTIVE AGENT ENGINE
              +------------------------------+------------------------------+
              |                              |                              |
              v                              v                              v
     Answer Evaluator              Question Generator             Feedback Generator
    (Quality & Action)            (Mistral AI Prompt)            (Structured Report)
              |                              |                              |
              +------------------------------+------------------------------+
                                             |
                                             v
                                  MISTRAL AI LLM ENGINE
                              (mistral-small-latest / SDK)
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic v2
- **Agent Framework**: LangGraph (`StateGraph`), LangChain Core
- **LLM Engine**: Mistral AI SDK (`mistralai`), Structured JSON Mode (`mistral-small-latest`)
- **Frontend**: React 18, Vite, React Router DOM, Vanilla CSS3 (Custom Cyber-Teal Dark Mode Design System)
- **Deployment**: Render (Backend Web Service), Vercel (Frontend SPA)
- **Testing**: Pytest test suite (13 passing tests)

---

## 🚀 Local Development Setup

### 1. Environment Setup

Clone the repository and activate virtual environment:

```bash
git clone https://github.com/itskrishn07/AI-Interview-Agent.git
cd "AI Interview Agent"

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set up `.env` configuration:

```bash
cp .env.example .env
# Edit .env and set MISTRAL_API_KEY
```

---

### 2. Run the FastAPI Backend

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend endpoints:
- Health Check: `GET http://localhost:8000/health`
- Live Interview API: `POST http://localhost:8000/api/interview`
- API Docs: `http://localhost:8000/docs`

---

### 3. Run the React Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## 🧪 Testing & Verification

Run the test suite with `pytest`:

```bash
pytest tests/ -v
```

### Test Suite Breakdown (13/13 Passing):
- `tests/test_api_contract.py`: API endpoints, session creation, turn continuation, and missing session 404 handling.
- `tests/test_candidate_analyzer.py`: Experience level classification & learning signal extraction.
- `tests/test_curriculum_retriever.py`: Day lookups & objective formatting.
- `tests/test_interview_engine.py`: Multi-turn interview lifecycle & feedback generation.
- `tests/test_langgraph_engine.py`: LangGraph node execution, state persistence & completion router rules.

---

## 📄 API Specification (`POST /api/interview`)

### Start Interview
```json
POST /api/interview

{
  "sessionId": "session-123",
  "candidate": { ... candidate profile ... }
}
```

**Response:**
```json
{
  "reply": "Welcome Sarah! Let's begin with your work on Embeddings...",
  "done": false
}
```

### Continue Turn
```json
POST /api/interview

{
  "sessionId": "session-123",
  "message": "We used cosine similarity with OpenAI text-embedding-3-small vectors..."
}
```

**Response (In Progress):**
```json
{
  "reply": "Solid response. Suppose query latency increases by 5x under high load...",
  "done": false
}
```

**Response (Completion - 8+ questions & 4+ days covered):**
```json
{
  "reply": "Thank you Sarah! That completes our technical interview session.",
  "done": true,
  "feedback": {
    "summary": "Sarah demonstrated strong senior-level understanding of vector retrieval...",
    "strengths": ["Clear explanation of embedding distance metrics and chunking strategies."],
    "gaps": ["Could elaborate further on distributed vector index scaling and monitoring."],
    "next": ["Review Curriculum Day 28 (Docker/Kubernetes Deployment) and Day 29 (Observability)."]
  }
}
```
