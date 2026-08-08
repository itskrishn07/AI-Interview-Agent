from typing import Dict, Any, List
from backend.services.llm_service import llm_service
from backend.prompts.evaluator import SYSTEM_EVALUATOR_PROMPT
from backend.services.candidate_analyzer import CandidateProfile

class AnswerEvaluation(BaseModel if False else object):
    pass

class AnswerEvaluator:
    """Evaluates candidate answers for depth, correctness, strengths, gaps, and next action."""
    
    def evaluate(
        self,
        candidate_profile: CandidateProfile,
        day_summary: str,
        question: str,
        answer: str,
        history: List[Dict[str, Any]],
        turns_on_current_day: int = 1
    ) -> Dict[str, Any]:
        
        # 1. Attempt LLM evaluation if available
        if llm_service.is_available():
            system_prompt = SYSTEM_EVALUATOR_PROMPT.format(
                candidate_name=candidate_profile.name,
                candidate_role=candidate_profile.role,
                experience_level=candidate_profile.experience_level,
                day_summary=day_summary,
                question=question,
                answer=answer,
                history_summary=str(history[-3:]) if history else "None"
            )
            schema_desc = """
            {
              "quality": "weak" | "moderate" | "strong" | "excellent",
              "score": 1..5,
              "reasoning": "string",
              "strengths": ["string"],
              "gaps": ["string"],
              "recommended_next_action": "DEEPER_FOLLOWUP" | "CLARIFICATION" | "FOUNDATIONAL" | "NEW_TOPIC" | "SCENARIO_TRADEOFF"
            }
            """
            result = llm_service.generate_structured(system_prompt, f"Question: {question}\nAnswer: {answer}", schema_desc)
            if result and "quality" in result and "recommended_next_action" in result:
                # Force new topic if already asked 2 questions on this topic
                if turns_on_current_day >= 2 and result["recommended_next_action"] != "NEW_TOPIC":
                    result["recommended_next_action"] = "NEW_TOPIC"
                return result

        # 2. Heuristic fallback evaluation (for offline/testing or API fallbacks)
        words = answer.strip().split()
        word_count = len(words)
        answer_lower = answer.lower()

        if word_count < 8 or "don't know" in answer_lower or "not sure" in answer_lower:
            quality = "weak"
            score = 2
            reasoning = "Candidate provided a brief or uncertain response."
            strengths = []
            gaps = ["Lack of depth or explanation in candidate response."]
            action = "FOUNDATIONAL"
        elif word_count > 35 or any(term in answer_lower for term in ["because", "trade-off", "architecture", "embedding", "vector", "pipeline", "rag", "mcp", "latency"]):
            quality = "strong" if word_count < 80 else "excellent"
            score = 4 if quality == "strong" else 5
            reasoning = "Candidate provided a detailed technical explanation with relevant domain concepts."
            strengths = ["Demonstrated clear domain understanding and structured explanation."]
            gaps = []
            action = "SCENARIO_TRADEOFF" if candidate_profile.experience_level == "senior" else "DEEPER_FOLLOWUP"
        else:
            quality = "moderate"
            score = 3
            reasoning = "Candidate provided a reasonable basic response."
            strengths = ["Basic operational understanding demonstrated."]
            gaps = ["Could provide more technical implementation detail."]
            action = "CLARIFICATION"

        if turns_on_current_day >= 2:
            action = "NEW_TOPIC"

        return {
            "quality": quality,
            "score": score,
            "reasoning": reasoning,
            "strengths": strengths,
            "gaps": gaps,
            "recommended_next_action": action
        }

answer_evaluator = AnswerEvaluator()
