from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status
from typing import Optional

from app.models.candidate import Candidate
from app.models.evaluation import Evaluation
from app.schemas.candidate import CandidateCreate, CandidateUpdate


def _get_or_404(db: Session, candidate_id: int) -> Candidate:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Candidate {candidate_id} not found")
    return candidate


def create_candidate(db: Session, payload: CandidateCreate) -> Candidate:
    if db.query(Candidate).filter(Candidate.email == payload.email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, f"Email '{payload.email}' already registered")
    candidate = Candidate(**payload.model_dump())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def get_all_candidates(db: Session, role: Optional[str] = None, page: int = 1, page_size: int = 10):
    q = db.query(Candidate)
    if role:
        q = q.filter(Candidate.role.ilike(f"%{role}%"))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total":       total,
        "page":        page,
        "page_size":   page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "items":       items,
    }


def get_candidate_by_id(db: Session, candidate_id: int) -> Candidate:
    return _get_or_404(db, candidate_id)


def update_candidate(db: Session, candidate_id: int, payload: CandidateUpdate) -> Candidate:
    candidate   = _get_or_404(db, candidate_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != candidate.email:
        if db.query(Candidate).filter(Candidate.email == update_data["email"]).first():
            raise HTTPException(status.HTTP_409_CONFLICT, f"Email '{update_data['email']}' already in use")

    for field, value in update_data.items():
        setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)
    return candidate


def delete_candidate(db: Session, candidate_id: int) -> dict:
    candidate = _get_or_404(db, candidate_id)
    db.delete(candidate)
    db.commit()
    return {"message": f"Candidate '{candidate.name}' deleted"}


def get_candidate_rankings(db: Session):
    rows = (
        db.query(
            Candidate.id,
            Candidate.name,
            Candidate.email,
            Candidate.role,
            Candidate.experience,
            func.avg(Evaluation.final_score).label("avg_final_score"),
            func.count(Evaluation.id).label("total_evaluations"),
        )
        .outerjoin(Evaluation, Evaluation.candidate_id == Candidate.id)
        .group_by(Candidate.id)
        .order_by(desc("avg_final_score"))
        .all()
    )
    return [
        {
            "rank":              i + 1,
            "id":                r.id,
            "name":              r.name,
            "email":             r.email,
            "role":              r.role,
            "experience":        r.experience,
            "avg_final_score":   round(r.avg_final_score, 2) if r.avg_final_score else None,
            "total_evaluations": r.total_evaluations,
        }
        for i, r in enumerate(rows)
    ]
