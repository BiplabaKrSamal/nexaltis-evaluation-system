from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.evaluation import Evaluation
from app.models.candidate import Candidate
from app.schemas.evaluation import EvaluationCreate, EvaluationUpdate


def _get_candidate_or_404(db: Session, candidate_id: int) -> Candidate:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Candidate {candidate_id} not found")
    return candidate


def _get_evaluation_or_404(db: Session, evaluation_id: int) -> Evaluation:
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Evaluation {evaluation_id} not found")
    return evaluation


def create_evaluation(db: Session, payload: EvaluationCreate) -> Evaluation:
    _get_candidate_or_404(db, payload.candidate_id)
    evaluation = Evaluation(**payload.model_dump())
    evaluation.final_score = evaluation.calculate_final_score()
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation


def get_evaluations_by_candidate(db: Session, candidate_id: int) -> list[Evaluation]:
    _get_candidate_or_404(db, candidate_id)
    return (
        db.query(Evaluation)
        .filter(Evaluation.candidate_id == candidate_id)
        .order_by(Evaluation.created_at.desc())
        .all()
    )


def get_evaluation_by_id(db: Session, evaluation_id: int) -> Evaluation:
    return _get_evaluation_or_404(db, evaluation_id)


def update_evaluation(db: Session, evaluation_id: int, payload: EvaluationUpdate) -> Evaluation:
    evaluation = _get_evaluation_or_404(db, evaluation_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(evaluation, field, value)
    evaluation.final_score = evaluation.calculate_final_score()
    db.commit()
    db.refresh(evaluation)
    return evaluation
