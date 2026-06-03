from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

_score     = Field(...,  ge=0, le=10)
_score_opt = Field(None, ge=0, le=10)


class EvaluationBase(BaseModel):
    communication:    float           = _score
    technical:        float           = _score
    problem_solving:  float           = _score
    ownership:        float           = _score
    comments:         Optional[str]   = None
    interviewer_name: Optional[str]   = Field(None, max_length=255)


class EvaluationCreate(EvaluationBase):
    candidate_id: int = Field(..., gt=0)


class EvaluationUpdate(BaseModel):
    communication:    Optional[float] = _score_opt
    technical:        Optional[float] = _score_opt
    problem_solving:  Optional[float] = _score_opt
    ownership:        Optional[float] = _score_opt
    comments:         Optional[str]   = None
    interviewer_name: Optional[str]   = Field(None, max_length=255)


class EvaluationResponse(EvaluationBase):
    id:          int
    candidate_id:int
    final_score: float
    created_at:  datetime
    updated_at:  datetime

    model_config = {"from_attributes": True}
