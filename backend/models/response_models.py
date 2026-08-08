from typing import Optional, List
from pydantic import BaseModel, Field

class FeedbackModel(BaseModel):
    summary: str = Field(..., description="Overall summary of the candidate's interview performance")
    strengths: List[str] = Field(default_factory=list, description="Specific, evidence-based strengths observed")
    gaps: List[str] = Field(default_factory=list, description="Specific areas where knowledge or reasoning fell short")
    next: List[str] = Field(default_factory=list, description="Actionable next steps and curriculum recommendations")

class InterviewResponse(BaseModel):
    reply: str = Field(..., description="The interviewer's next question, response, or conclusion message")
    done: bool = Field(..., description="Flag indicating whether the interview has concluded")
    feedback: Optional[FeedbackModel] = Field(default=None, description="Final structured feedback (populated only when done is true)")
