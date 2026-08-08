from typing import Dict, Any, List
from backend.services.llm_service import llm_service
from backend.prompts.feedback import SYSTEM_FEEDBACK_PROMPT
from backend.services.candidate_analyzer import CandidateProfile
from backend.models.interview_state import InterviewState

class FeedbackGenerator:
    """Generates evidence-based, actionable final interview feedback."""

    def generate_feedback(
        self,
        candidate_profile: CandidateProfile,
        session: InterviewState
    ) -> Dict[str, Any]:
        
        # 1. Prepare transcript summary and accumulated evidence
        transcript_lines = []
        for record in session.history:
            transcript_lines.append(
                f"Day {record.day} ({record.day_title}) | Q: {record.question} | A: {record.answer} | Score: {record.score}/5 | Evaluation: {record.reasoning}"
            )
        transcript_text = "\n".join(transcript_lines)

        # 2. Attempt LLM feedback generation if available
        if llm_service.is_available():
            system_prompt = SYSTEM_FEEDBACK_PROMPT.format(
                candidate_name=candidate_profile.name,
                candidate_role=candidate_profile.role,
                years_experience=candidate_profile.years_experience,
                experience_level=candidate_profile.experience_level,
                interview_transcript=transcript_text,
                accumulated_strengths="\n- ".join(session.strengths_accumulated) if session.strengths_accumulated else "None",
                accumulated_gaps="\n- ".join(session.gaps_accumulated) if session.gaps_accumulated else "None"
            )
            schema_desc = """
            {
              "summary": "string",
              "strengths": ["string"],
              "gaps": ["string"],
              "next": ["string"]
            }
            """
            user_prompt = "Synthesize the candidate's performance into final structured feedback."
            result = llm_service.generate_structured(system_prompt, user_prompt, schema_desc)
            if result and all(k in result for k in ["summary", "strengths", "gaps", "next"]):
                return result

        # 3. Deterministic fallback feedback synthesis
        strengths = list(set(session.strengths_accumulated))
        if not strengths:
            strengths = [
                f"Demonstrated solid engagement across {len(session.covered_days)} curriculum topics.",
                f"Provided practical insights relevant to role as {candidate_profile.role}."
            ]

        gaps = list(set(session.gaps_accumulated))
        if not gaps:
            gaps = [
                "Could elaborate further on production edge-cases and error handling strategies."
            ]

        next_steps = []
        covered_set = set(session.covered_days)
        # Recommend skipped or uncovered days from profile
        for d in candidate_profile.skipped_days + [7, 10, 16, 22, 23, 28]:
            if d not in covered_set and len(next_steps) < 3:
                next_steps.append(f"Review Curriculum Day {d} to strengthen core concepts.")

        if not next_steps:
            next_steps = [
                "Review advanced RAG optimization and production monitoring techniques (Days 26-29).",
                "Practice explaining architectural trade-offs in distributed agentic systems."
            ]

        summary = (
            f"{candidate_profile.name} completed a technical interview covering {session.question_count} questions "
            f"across {len(session.covered_days)} distinct curriculum days (Days {', '.join(map(str, sorted(session.covered_days)))}). "
            f"Overall performance reflected {candidate_profile.experience_level}-level understanding as a {candidate_profile.role}."
        )

        return {
            "summary": summary,
            "strengths": strengths,
            "gaps": gaps,
            "next": next_steps
        }

feedback_generator = FeedbackGenerator()
