from fastapi import APIRouter, HTTPException, status
from backend.models.request_models import InterviewRequest
from backend.models.response_models import InterviewResponse, FeedbackModel
from backend.services.session_manager import session_manager
from backend.services.interview_manager import interview_manager

router = APIRouter()

@router.post("/interview", response_model=InterviewResponse)
async def handle_interview(req: InterviewRequest):
    """
    Core HTTP endpoint specified in technical-spec.md.
    Supports starting an interview, continuing multi-turn interview turns, and concluding with feedback.
    """
    # 1. Start Interview flow
    if req.candidate is not None:
        reply, done, feedback = interview_manager.start_interview(req.sessionId, req.candidate)
        return InterviewResponse(
            reply=reply,
            done=done,
            feedback=FeedbackModel(**feedback) if feedback else None
        )

    # 2. Continue Interview flow
    session = session_manager.get_session(req.sessionId)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session '{req.sessionId}' not found. Please start an interview with candidate data."
        )

    if session.done:
        feedback_data = session.feedback or {
            "summary": "Interview completed.",
            "strengths": session.strengths_accumulated,
            "gaps": session.gaps_accumulated,
            "next": []
        }
        return InterviewResponse(
            reply="The interview has already been completed.",
            done=True,
            feedback=FeedbackModel(**feedback_data)
        )

    if req.message is None or not req.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A non-empty candidate message is required to continue the interview."
        )

    reply, done, feedback = interview_manager.continue_interview(req.sessionId, req.message.strip())

    return InterviewResponse(
        reply=reply,
        done=done,
        feedback=FeedbackModel(**feedback) if feedback else None
    )
