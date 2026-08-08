import logging
from typing import Dict, Any, Tuple, Optional, List
from backend.services.session_manager import session_manager
from backend.services.candidate_analyzer import candidate_analyzer
from backend.services.curriculum_retriever import curriculum_retriever
from backend.services.question_generator import question_generator
from backend.services.answer_evaluator import answer_evaluator
from backend.services.feedback_generator import feedback_generator
from backend.models.interview_state import InterviewState, TurnRecord

logger = logging.getLogger(__name__)

class InterviewManager:
    """Core interview decision engine orchestrating adaptive conversation loop."""
    
    # Priority curriculum days for coverage if candidate lacks specific probe days
    CORE_CURRICULUM_DAYS = [7, 8, 10, 12, 16, 22, 23, 28]

    def _select_initial_day(self, candidate_profile) -> int:
        if candidate_profile.probe_days:
            return candidate_profile.probe_days[0]
        if candidate_profile.completed_days:
            return candidate_profile.completed_days[0]
        return 7

    def _select_next_day(self, state: InterviewState, candidate_profile) -> int:
        covered = set(state.covered_days)
        
        # 1. Prefer uncovered probe days (multi-attempt or skipped days)
        for day in candidate_profile.probe_days:
            if day not in covered:
                return day

        # 2. Prefer uncovered core curriculum days
        for day in self.CORE_CURRICULUM_DAYS:
            if day not in covered:
                return day

        # 3. Prefer any uncovered curriculum day
        all_days = curriculum_retriever.get_available_day_numbers()
        for day in all_days:
            if day not in covered:
                return day

        # 4. Fallback: select least recently visited day
        return state.covered_days[0] if state.covered_days else 7

    def start_interview(self, session_id: str, raw_candidate: Dict[str, Any]) -> Tuple[str, bool, Optional[Dict[str, Any]]]:
        """Initializes a new interview session and generates the first question."""
        profile = candidate_analyzer.analyze(raw_candidate)
        session = session_manager.create_session(session_id, raw_candidate)

        initial_day = self._select_initial_day(profile)
        session.current_day = initial_day
        session.covered_days = [initial_day]
        session.question_count = 1

        first_question = question_generator.generate_question(
            candidate_profile=profile,
            day_num=initial_day,
            question_count=1,
            covered_days=session.covered_days,
            action_decision="NEW_TOPIC"
        )
        session.current_question = first_question
        session_manager.update_session(session)

        return first_question, False, None

    def continue_interview(self, session_id: str, candidate_message: str) -> Tuple[str, bool, Optional[Dict[str, Any]]]:
        """Processes candidate answer, evaluates response, decides next action, and advances state."""
        session = session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        if session.done:
            return "Interview completed.", True, session.feedback

        profile = candidate_analyzer.analyze(session.candidate)

        # 1. Calculate turns on current day
        current_day = session.current_day or 7
        day_info = curriculum_retriever.get_day(current_day) or {}
        day_title = day_info.get("title", f"Day {current_day}")

        turns_on_current_day = sum(1 for rec in session.history if rec.day == current_day) + 1

        # 2. Evaluate answer
        eval_result = answer_evaluator.evaluate(
            candidate_profile=profile,
            day_summary=curriculum_retriever.format_day_summary(current_day),
            question=session.current_question or "",
            answer=candidate_message,
            history=[rec.model_dump() for rec in session.history],
            turns_on_current_day=turns_on_current_day
        )

        # 3. Record turn in history
        turn_record = TurnRecord(
            turn_index=session.question_count,
            day=current_day,
            day_title=day_title,
            question=session.current_question or "",
            answer=candidate_message,
            quality=eval_result.get("quality"),
            score=eval_result.get("score"),
            reasoning=eval_result.get("reasoning"),
            strengths=eval_result.get("strengths", []),
            gaps=eval_result.get("gaps", []),
            recommended_next_action=eval_result.get("recommended_next_action")
        )
        session.history.append(turn_record)

        # Accumulate strengths and gaps
        session.strengths_accumulated.extend(eval_result.get("strengths", []))
        session.gaps_accumulated.extend(eval_result.get("gaps", []))

        # 4. Check HARD REQUIREMENTS for completion:
        # question_count >= 8 AND len(covered_days) >= 4
        distinct_days_count = len(set(session.covered_days))
        next_action = eval_result.get("recommended_next_action", "NEW_TOPIC")

        # Force topic switch if 2 turns spent on current topic and distinct days < 4
        if turns_on_current_day >= 2 and distinct_days_count < 4:
            next_action = "NEW_TOPIC"

        if session.question_count >= 8 and distinct_days_count >= 4 and (next_action == "NEW_TOPIC" or session.question_count >= 10):
            # Conclude interview and generate structured feedback
            feedback_data = feedback_generator.generate_feedback(profile, session)
            session.done = True
            session.feedback = feedback_data
            session_manager.update_session(session)
            return "Thank you! That completes all technical questions for your interview. Here is your structured feedback.", True, feedback_data

        # 5. Prepare next turn
        session.question_count += 1
        if next_action == "NEW_TOPIC" or turns_on_current_day >= 2:
            next_day = self._select_next_day(session, profile)
            session.current_day = next_day
            if next_day not in session.covered_days:
                session.covered_days.append(next_day)

        next_q = question_generator.generate_question(
            candidate_profile=profile,
            day_num=session.current_day,
            question_count=session.question_count,
            covered_days=session.covered_days,
            action_decision=next_action,
            previous_question=session.current_question or "",
            previous_answer=candidate_message
        )

        session.current_question = next_q
        session_manager.update_session(session)

        return next_q, False, None

interview_manager = InterviewManager()
