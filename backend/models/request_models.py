from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class InterviewRequest(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier for the interview")
    candidate: Optional[Dict[str, Any]] = Field(default=None, description="Candidate data passed on interview initialization")
    message: Optional[str] = Field(default=None, description="Candidate response message during interview conversation")
