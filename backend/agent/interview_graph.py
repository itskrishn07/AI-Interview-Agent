import logging
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from backend.services.candidate_analyzer import candidate_analyzer, CandidateProfile
from backend.services.curriculum_retriever import curriculum_retriever
from backend.services.question_generator import question_generator
from backend.services.answer_evaluator import answer_evaluator
from backend.services.feedback_generator import feedback_generator
from backend.models.interview_state import InterviewState, TurnRecord

logger = logging.getLogger(__name__)

class InterviewGraphState(TypedDict, total=False):
    session_id: str
    candidate_raw: Dict[str, Any]
    candidate_profile: Optional[Dict[str, Any]]
    question_count: int
    covered_days: List[int]
    current_day: Optional[int]
    current_question: Optional[str]
    candidate_message: Optional[str]
    latest_evaluation: Optional[Dict[str, Any]]
    history: List[Dict[str, Any]]
    strengths: List[str]
    gaps: List[str]
    done: bool
    feedback: Optional[Dict[str, Any]]
    reply: str

# Priority curriculum days for coverage fallback
CORE_CURRICULUM_DAYS = [7, 8, 10, 12, 16, 22, 23, 28]

def _dict_to_profile(profile_dict: Dict[str, Any]) -> CandidateProfile:
    return CandidateProfile(**profile_dict)

# 1. Analyze Candidate Node
def analyze_candidate_node(state: InterviewGraphState) -> Dict[str, Any]:
    if "candidate_profile" not in state or not state["candidate_profile"]:
        profile = candidate_analyzer.analyze(state["candidate_raw"])
        return {"candidate_profile": profile.model_dump()}
    return {}

# 2. Evaluate Answer Node
def evaluate_answer_node(state: InterviewGraphState) -> Dict[str, Any]:
    msg = state.get("candidate_message")
    if not msg or not msg.strip():
        return {}

    profile = _dict_to_profile(state["candidate_profile"])
    current_day = state.get("current_day", 7)
    day_info = curriculum_retriever.get_day(current_day) or {}
    day_title = day_info.get("title", f"Day {current_day}")

    history = state.get("history", [])
    turns_on_current_day = sum(1 for rec in history if rec.get("day") == current_day) + 1

    eval_result = answer_evaluator.evaluate(
        candidate_profile=profile,
        day_summary=curriculum_retriever.format_day_summary(current_day),
        question=state.get("current_question", ""),
        answer=msg.strip(),
        history=history,
        turns_on_current_day=turns_on_current_day
    )

    turn_record = {
        "turn_index": state.get("question_count", 1),
        "day": current_day,
        "day_title": day_title,
        "question": state.get("current_question", ""),
        "answer": msg.strip(),
        "quality": eval_result.get("quality"),
        "score": eval_result.get("score"),
        "reasoning": eval_result.get("reasoning"),
        "strengths": eval_result.get("strengths", []),
        "gaps": eval_result.get("gaps", []),
        "recommended_next_action": eval_result.get("recommended_next_action")
    }

    updated_history = history + [turn_record]
    updated_strengths = list(state.get("strengths", [])) + eval_result.get("strengths", [])
    updated_gaps = list(state.get("gaps", [])) + eval_result.get("gaps", [])

    return {
        "latest_evaluation": eval_result,
        "history": updated_history,
        "strengths": updated_strengths,
        "gaps": updated_gaps
    }

# 3. Conditional Completion Router
def should_complete_router(state: InterviewGraphState) -> str:
    question_count = state.get("question_count", 1)
    covered_days = state.get("covered_days", [])
    distinct_days = len(set(covered_days))
    
    latest_eval = state.get("latest_evaluation", {})
    next_action = latest_eval.get("recommended_next_action", "NEW_TOPIC")

    # Hard Requirements Enforcement: question_count >= 8 AND distinct_days >= 4
    if question_count >= 8 and distinct_days >= 4 and (next_action == "NEW_TOPIC" or question_count >= 10):
        return "generate_feedback"
    return "select_topic"

# 4. Select Topic Node
def select_topic_node(state: InterviewGraphState) -> Dict[str, Any]:
    # Initial start turn
    if state.get("question_count", 0) == 0:
        profile = _dict_to_profile(state["candidate_profile"])
        initial_day = profile.probe_days[0] if profile.probe_days else (profile.completed_days[0] if profile.completed_days else 7)
        return {
            "current_day": initial_day,
            "covered_days": [initial_day],
            "question_count": 1
        }

    # Continuation turn
    q_count = state.get("question_count", 1) + 1
    covered = set(state.get("covered_days", []))
    current_day = state.get("current_day", 7)

    latest_eval = state.get("latest_evaluation", {})
    next_action = latest_eval.get("recommended_next_action", "NEW_TOPIC")
    history = state.get("history", [])
    turns_on_current_day = sum(1 for rec in history if rec.get("day") == current_day)

    # Force topic shift if 2 turns spent on current topic
    if turns_on_current_day >= 2 or next_action == "NEW_TOPIC":
        profile = _dict_to_profile(state["candidate_profile"])
        next_day = None
        
        # 1. Probe days
        for d in profile.probe_days:
            if d not in covered:
                next_day = d
                break
        
        # 2. Core curriculum days
        if not next_day:
            for d in CORE_CURRICULUM_DAYS:
                if d not in covered:
                    next_day = d
                    break

        # 3. Any curriculum day
        if not next_day:
            all_days = curriculum_retriever.get_available_day_numbers()
            for d in all_days:
                if d not in covered:
                    next_day = d
                    break

        if not next_day:
            next_day = current_day

        updated_covered = list(state.get("covered_days", []))
        if next_day not in updated_covered:
            updated_covered.append(next_day)

        return {
            "current_day": next_day,
            "covered_days": updated_covered,
            "question_count": q_count
        }

    return {
        "question_count": q_count
    }

# 5. Generate Question Node
def generate_question_node(state: InterviewGraphState) -> Dict[str, Any]:
    profile = _dict_to_profile(state["candidate_profile"])
    current_day = state.get("current_day", 7)
    latest_eval = state.get("latest_evaluation", {})
    action = latest_eval.get("recommended_next_action", "NEW_TOPIC")

    question = question_generator.generate_question(
        candidate_profile=profile,
        day_num=current_day,
        question_count=state.get("question_count", 1),
        covered_days=state.get("covered_days", []),
        action_decision=action,
        previous_question=state.get("current_question", ""),
        previous_answer=state.get("candidate_message", "")
    )

    return {
        "current_question": question,
        "reply": question,
        "done": False
    }

# 6. Generate Feedback Node
def generate_feedback_node(state: InterviewGraphState) -> Dict[str, Any]:
    profile = _dict_to_profile(state["candidate_profile"])
    
    # Reconstruct InterviewState model for feedback generator compatibility
    turn_records = [TurnRecord(**rec) for rec in state.get("history", [])]
    mock_session = InterviewState(
        session_id=state.get("session_id", "session-temp"),
        candidate=state.get("candidate_raw", {}),
        question_count=state.get("question_count", 8),
        covered_days=state.get("covered_days", []),
        history=turn_records,
        strengths_accumulated=state.get("strengths", []),
        gaps_accumulated=state.get("gaps", [])
    )

    feedback_data = feedback_generator.generate_feedback(profile, mock_session)

    return {
        "done": True,
        "feedback": feedback_data,
        "reply": "Thank you! That completes all technical questions for your interview. Here is your structured feedback."
    }

# Construct State Graph
workflow = StateGraph(InterviewGraphState)

workflow.add_node("analyze_candidate", analyze_candidate_node)
workflow.add_node("evaluate_answer", evaluate_answer_node)
workflow.add_node("select_topic", select_topic_node)
workflow.add_node("generate_question", generate_question_node)
workflow.add_node("generate_feedback", generate_feedback_node)

workflow.set_entry_point("analyze_candidate")

workflow.add_edge("analyze_candidate", "evaluate_answer")

workflow.add_conditional_edges(
    "evaluate_answer",
    should_complete_router,
    {
        "generate_feedback": "generate_feedback",
        "select_topic": "select_topic"
    }
)

workflow.add_edge("select_topic", "generate_question")
workflow.add_edge("generate_question", END)
workflow.add_edge("generate_feedback", END)

interview_agent_graph = workflow.compile()
