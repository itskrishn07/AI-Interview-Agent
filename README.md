# AI Technical Interview Agent — ABTalks Hackathon

An adaptive, realistic, multi-turn AI Technical Interviewer built for the **ABTalks Hackathon**.

The AI Interview Agent conducts personalized technical interviews based on a candidate's learning journey throughout the 31-day AI Cohort curriculum (covering RAG, Vector Databases, Prompting, Function Calling, Agents, MCP, Deployment, Observability).

---

## 🌟 Key Features

- **Candidate Intelligence**: Parses candidate profiles from `candidates.json`, analyzing experience level, completed missions, first-try successes, skipped topics, and attempt history to extract learning signals.
- **Adaptive Interview Loop**: Dynamic follow-up routing (`DEEPER_FOLLOWUP`, `CLARIFICATION`, `FOUNDATIONAL`, `NEW_TOPIC`, `SCENARIO_TRADEOFF`) based on previous answer quality and role seniority.
- **Deterministic Curriculum Grounding**: Selectively retrieves objectives and tools from `curriculum.json` without dumping unnecessary context into LLM prompts.
- **Strict Code-Level Hard Constraints**: Enforces `minimum_questions >= 8` AND `minimum_curriculum_days >= 4` in application logic before an interview can conclude (`done = true`).
- **Evidence-Based Feedback**: Generates structured, actionable feedback (`summary`, `strengths`, `gaps`, `next`) upon interview completion.
- **Full API Specification Compliance**: Exposes `POST /api/interview` matching [`technical-spec.md`](technical-spec.md).
- **Interactive Streamlit UI**: Polished dark-mode web application featuring candidate selector, turn-by-turn chat interface, live progress tracking bar, and feedback dashboard cards.

---

## 📐 Architecture Overview

```text
                                 FRONTEND
                     Streamlit Dashboard / UI (app.py)
                                     |
                                     v
                           FastAPI Backend (main.py)
                                     |
                                     v
                        API Endpoint (/api/interview)
                                     |
                                     v
                           Interview Manager
                                     |
          +--------------------------+--------------------------+
          |                          |                          |
          v                          v                          v
  Candidate Analyzer       Curriculum Retriever        Session Manager
 (Learning Signals)       (Structured Lookup)        (State Persistence)
          |                          |                          |
          +--------------------------+--------------------------+
                                     |
                                     v
                              Interview Agent
                                     |
          +--------------------------+--------------------------+
          |                          |                          |
          v                          v                          v
  Question Generator         Answer Evaluator           Feedback Generator
 (Adaptive Strategy)         (Quality & Gaps)          (Structured Report)
          |                          |                          |
          +--------------------------+--------------------------+
                                     |
                                     v
                             LLM Service (Mistral AI)
```

---

## 🚀 Getting Started

### 1. Environment Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set up environment variables:

```bash
cp .env.example .env
# Add your MISTRAL_API_KEY to .env (e.g. MISTRAL_API_KEY=your_key, MISTRAL_MODEL=mistral-small-latest)
# Optional: App also supports OPENAI_API_KEY or falls back gracefully to heuristic generation if no key is set
```

---

### 2. Run the Backend API

Start the FastAPI backend server on `http://localhost:8000`:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend endpoints:
- Health Check: `GET http://localhost:8000/health`
- Interview Endpoint: `POST http://localhost:8000/api/interview`

---

### 3. Run the Streamlit Frontend UI

In a new terminal window:

```bash
streamlit run frontend/app.py
```

Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Verification

Run the comprehensive test suite with `pytest`:

```bash
pytest tests/ -v
```

Test coverage includes:
- `tests/test_api_contract.py`: Endpoint request/response verification & session lifecycle.
- `tests/test_candidate_analyzer.py`: Learning signal extraction & experience level classification.
- `tests/test_curriculum_retriever.py`: Curriculum loading & day lookups.
- `tests/test_interview_engine.py`: Full multi-turn end-to-end interview simulation (8+ questions, 4+ days, adaptive difficulty, structured feedback).

---

## 📄 API Specification (`POST /api/interview`)

### Start Interview
```json
POST /api/interview

{
  "sessionId": "session-123",
  "candidate": { ... candidate data ... }
}
```
**Response:**
```json
{
  "reply": "Welcome to your technical interview...",
  "done": false
}
```

### Continue Turn
```json
POST /api/interview

{
  "sessionId": "session-123",
  "message": "Candidate's technical response..."
}
```
**Response (In progress):**
```json
{
  "reply": "Follow-up question or new topic question...",
  "done": false
}
```

**Response (Completion):**
```json
{
  "reply": "Thank you! That completes all technical questions...",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": ["..."],
    "gaps": ["..."],
    "next": ["..."]
  }
}
```
