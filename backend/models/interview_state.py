from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TurnRecord(BaseModel):
    turn_index: int
    day: int
    day_title: str
    question: str
    answer: Optional[str] = None
    quality: Optional[str] = None # weak, moderate, strong, excellent
    score: Optional[int] = None # 1 to 5
    reasoning: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    recommended_next_action: Optional[str] = None

class InterviewState(BaseModel):
    session_id: str
    candidate: Dict[str, Any]
    question_count: int = 0
    covered_days: List[int] = Field(default_factory=list)
    current_day: Optional[int] = None
    current_question: Optional[str] = None
    current_difficulty: str = "moderate" # foundational, moderate, deeper, scenario
    history: List[TurnRecord] = Field(default_factory=list)
    strengths_accumulated: List[str] = Field(default_factory=list)
    gaps_accumulated: List[str] = Field(default_factory=list)
    done: bool = False
    feedback: Optional[Dict[str, Any]] = None
