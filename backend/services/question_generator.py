from typing import Dict, Any, List
from backend.services.llm_service import llm_service
from backend.prompts.interviewer import SYSTEM_INTERVIEWER_PROMPT
from backend.services.candidate_analyzer import CandidateProfile
from backend.services.curriculum_retriever import curriculum_retriever

class QuestionGenerator:
    """Generates natural, adaptive, role-tailored technical interview questions."""
    
    FALLBACK_QUESTIONS: Dict[int, Dict[str, str]] = {
        1: {
            "initial": "To kick things off, how do you set up your Python virtual environment and debugging configuration for AI development?",
            "deeper": "How do you ensure proper isolation and dependency management across different Python environments?",
            "foundational": "What is the primary purpose of using a Python virtual environment (.venv) when starting a project?"
        },
        7: {
            "initial": "Let's discuss vector embeddings. When building a RAG application, how do text chunking choices impact the quality of generated embeddings?",
            "deeper": "How do distance metrics like Cosine Similarity vs Dot Product affect document retrieval accuracy in high-dimensional vector spaces?",
            "foundational": "In plain technical terms, what is a text embedding and why do we convert text into numerical vectors?"
        },
        8: {
            "initial": "When comparing vector databases like ChromaDB and Pinecone, what technical criteria guide your choice between local in-memory indices and managed cloud indices?",
            "deeper": "How do indexing algorithms like HNSW (Hierarchical Navigable Small World) balance query throughput against indexing memory overhead?",
            "foundational": "What core problem does a vector database solve that traditional relational SQL databases struggle with?"
        },
        10: {
            "initial": "In building a hybrid retrieval engine, how do you combine structured SQL queries with semantic vector search for complex queries?",
            "deeper": "How do you handle result deduplication, score normalization, and re-ranking across disparate retrieval sources?",
            "foundational": "What is the difference between keyword/structured search and semantic vector search?"
        },
        12: {
            "initial": "Prompt engineering is critical for RAG precision. How do you design system prompts to enforce strict grounding and prevent hallucinations?",
            "deeper": "When would you use Few-Shot prompting over Zero-Shot or Chain-of-Thought prompting for structured data extraction?",
            "foundational": "What is the difference between system prompts and user prompts in an LLM application?"
        },
        16: {
            "initial": "When designing a FastAPI backend for an AI chatbot, how do you manage session state and context history across HTTP requests?",
            "deeper": "How do you handle API timeouts, worker concurrency, and rate limiting when calling external LLM providers in FastAPI?",
            "foundational": "What endpoint structure would you design for a basic backend chat service?"
        },
        22: {
            "initial": "In multi-agent architectures, how do you design router agents to delegate sub-tasks to specialist agents efficiently?",
            "deeper": "How do you prevent infinite loops or cascading agent failures when multiple autonomous agents communicate?",
            "foundational": "What is the difference between a single LLM call and a multi-agent orchestrated workflow?"
        },
        23: {
            "initial": "Model Context Protocol (MCP) standardizes tool connectivity. How does an MCP server expose tools and resources to AI clients?",
            "deeper": "How do you handle tool authorization, payload validation, and error reporting inside an MCP integration?",
            "foundational": "What problem does the Model Context Protocol (MCP) solve for LLM integration?"
        },
        28: {
            "initial": "When deploying AI applications with Docker and Kubernetes, how do you manage environment variables, secrets, and health probes?",
            "deeper": "How do you handle GPU memory allocation and container scaling for local LLM or embedding workloads in Kubernetes?",
            "foundational": "Why is containerization useful when deploying backend AI services?"
        }
    }

    def generate_question(
        self,
        candidate_profile: CandidateProfile,
        day_num: int,
        question_count: int,
        covered_days: List[int],
        action_decision: str,
        previous_question: str = "",
        previous_answer: str = ""
    ) -> str:
        day_summary = curriculum_retriever.format_day_summary(day_num)

        # 1. Attempt LLM generation if available
        if llm_service.is_available():
            system_prompt = SYSTEM_INTERVIEWER_PROMPT.format(
                candidate_name=candidate_profile.name,
                candidate_role=candidate_profile.role,
                years_experience=candidate_profile.years_experience,
                experience_level=candidate_profile.experience_level,
                education=candidate_profile.education,
                day_summary=day_summary,
                question_count=question_count,
                covered_days=covered_days,
                action_decision=action_decision,
                previous_answer=previous_answer or "N/A"
            )
            user_prompt = f"Ask the next technical question for curriculum Day {day_num}. Decision directive: {action_decision}."
            if previous_question:
                user_prompt += f" Previous question: '{previous_question}'."
            
            question = llm_service.generate_text(system_prompt, user_prompt, temperature=0.7)
            if question and len(question.strip()) > 15:
                return question.strip()

        # 2. Heuristic fallback generation
        day_fallbacks = self.FALLBACK_QUESTIONS.get(day_num, {})
        if action_decision in ["DEEPER_FOLLOWUP", "SCENARIO_TRADEOFF"]:
            q = day_fallbacks.get("deeper")
        elif action_decision == "FOUNDATIONAL":
            q = day_fallbacks.get("foundational")
        else:
            q = day_fallbacks.get("initial")

        if not q:
            day_info = curriculum_retriever.get_day(day_num) or {}
            title = day_info.get("title", f"Day {day_num}")
            tools = ", ".join(day_info.get("tools", []))
            q = f"Let's move on to {title}. In your work with {tools}, how have you applied these concepts in production?"

        return q

question_generator = QuestionGenerator()
