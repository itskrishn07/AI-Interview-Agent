from typing import Dict, Optional, Any
from backend.models.interview_state import InterviewState

class SessionManager:
    """In-memory session manager for interview sessions."""
    def __init__(self):
        self._sessions: Dict[str, InterviewState] = {}

    def get_session(self, session_id: str) -> Optional[InterviewState]:
        return self._sessions.get(session_id)

    def create_session(self, session_id: str, candidate_data: Dict[str, Any]) -> InterviewState:
        session = InterviewState(
            session_id=session_id,
            candidate=candidate_data
        )
        self._sessions[session_id] = session
        return session

    def update_session(self, session: InterviewState) -> None:
        self._sessions[session.session_id] = session

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def clear_all(self) -> None:
        self._sessions.clear()

# Global singleton session manager
session_manager = SessionManager()
