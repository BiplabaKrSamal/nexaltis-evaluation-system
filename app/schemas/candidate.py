from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class CandidateBase(BaseModel):
    name:       str      = Field(..., min_length=1, max_length=255)
    email:      EmailStr
    role:       str      = Field(..., min_length=1, max_length=255)
    experience: int      = Field(..., ge=0)

    @field_validator("name", "role")
    @classmethod
    def strip_and_reject_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be blank")
        return v.strip()


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    name:       Optional[str]      = Field(None, min_length=1, max_length=255)
    email:      Optional[EmailStr] = None
    role:       Optional[str]      = Field(None, min_length=1, max_length=255)
    experience: Optional[int]      = Field(None, ge=0)

    @field_validator("name")
    @classmethod
    def strip_and_reject_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip() if v else v


class CandidateResponse(CandidateBase):
    id:         int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateRankingResponse(BaseModel):
    rank:              int
    id:                int
    name:              str
    email:             str
    role:              str
    experience:        int
    avg_final_score:   Optional[float] = None
    total_evaluations: int = 0

    model_config = {"from_attributes": True}


class PaginatedCandidates(BaseModel):
    total:       int
    page:        int
    page_size:   int
    total_pages: int
    items:       list[CandidateResponse]
