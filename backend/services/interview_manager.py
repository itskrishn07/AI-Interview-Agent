import logging
from typing import Dict, Any, Tuple, Optional
from backend.services.session_manager import session_manager
from backend.models.interview_state import TurnRecord
from backend.agent.interview_graph import interview_agent_graph, InterviewGraphState

logger = logging.getLogger(__name__)

class InterviewManager:
    """Core interview decision manager orchestrating agentic workflow via LangGraph."""

    def start_interview(self, session_id: str, raw_candidate: Dict[str, Any]) -> Tuple[str, bool, Optional[Dict[str, Any]]]:
        """Initializes a new session and executes the initial LangGraph workflow."""
        session = session_manager.create_session(session_id, raw_candidate)

        initial_state: InterviewGraphState = {
            "session_id": session_id,
            "candidate_raw": raw_candidate,
            "question_count": 0,
            "covered_days": [],
            "history": [],
            "strengths": [],
            "gaps": [],
            "done": False
        }

        result_state = interview_agent_graph.invoke(initial_state)

        # Sync back to in-memory session manager
        session.current_day = result_state.get("current_day")
        session.covered_days = result_state.get("covered_days", [])
        session.question_count = result_state.get("question_count", 1)
        session.current_question = result_state.get("current_question")
        session.done = result_state.get("done", False)
        session.feedback = result_state.get("feedback")

        session_manager.update_session(session)

        return result_state.get("reply", "Welcome to your technical interview."), session.done, session.feedback

    def continue_interview(self, session_id: str, candidate_message: str) -> Tuple[str, bool, Optional[Dict[str, Any]]]:
        """Processes candidate answer turn by invoking the compiled LangGraph workflow."""
        session = session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        if session.done:
            return "Interview completed.", True, session.feedback

        # Convert in-memory session into LangGraph state dictionary
        graph_input_state: InterviewGraphState = {
            "session_id": session.session_id,
            "candidate_raw": session.candidate,
            "question_count": session.question_count,
            "covered_days": session.covered_days,
            "current_day": session.current_day,
            "current_question": session.current_question,
            "candidate_message": candidate_message,
            "history": [rec.model_dump() for rec in session.history],
            "strengths": session.strengths_accumulated,
            "gaps": session.gaps_accumulated,
            "done": session.done,
            "feedback": session.feedback
        }

        result_state = interview_agent_graph.invoke(graph_input_state)

        # Sync result state back to SessionManager
        session.question_count = result_state.get("question_count", session.question_count)
        session.covered_days = result_state.get("covered_days", session.covered_days)
        session.current_day = result_state.get("current_day", session.current_day)
        session.current_question = result_state.get("current_question", session.current_question)
        session.strengths_accumulated = result_state.get("strengths", session.strengths_accumulated)
        session.gaps_accumulated = result_state.get("gaps", session.gaps_accumulated)
        session.done = result_state.get("done", False)
        session.feedback = result_state.get("feedback")

        if result_state.get("history"):
            turn_records = [TurnRecord(**item) for item in result_state["history"]]
            session.history = turn_records

        session_manager.update_session(session)

        return result_state.get("reply", "Thank you for your response."), session.done, session.feedback

interview_manager = InterviewManager()
