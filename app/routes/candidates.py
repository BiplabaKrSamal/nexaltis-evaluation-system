from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateRankingResponse,
    PaginatedCandidates,
)
from app.schemas.common import MessageResponse
from app.services import candidate_service
from app.auth import get_api_key

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key),
):
    return candidate_service.create_candidate(db, payload)


@router.get("/rankings", response_model=list[CandidateRankingResponse])
def get_rankings(
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key),
):
    return candidate_service.get_candidate_rankings(db)


@router.get("", response_model=PaginatedCandidates)
def get_candidates(
    role:      Optional[str] = Query(None),
    page:      int           = Query(1,  ge=1),
    page_size: int           = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _:  str     = Depends(get_api_key),
):
    return candidate_service.get_all_candidates(db, role=role, page=page, page_size=page_size)


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    _:  str     = Depends(get_api_key),
):
    return candidate_service.get_candidate_by_id(db, candidate_id)


@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
    _:  str     = Depends(get_api_key),
):
    return candidate_service.update_candidate(db, candidate_id, payload)


@router.delete("/{candidate_id}", response_model=MessageResponse)
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    _:  str     = Depends(get_api_key),
):
    return candidate_service.delete_candidate(db, candidate_id)
