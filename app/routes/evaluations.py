from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.evaluation import EvaluationCreate, EvaluationUpdate, EvaluationResponse
from app.services import evaluation_service
from app.auth import get_api_key

router = APIRouter(tags=["Evaluations"])


@router.post("/evaluations", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    payload: EvaluationCreate,
    db: Session = Depends(get_db),
    _:  str     = Depends(get_api_key),
):
    return evaluation_service.create_evaluation(db, payload)


@router.get("/candidates/{candidate_id}/evaluations", response_model=list[EvaluationResponse])
def get_candidate_evaluations(
    candidate_id: int,
    db: Session = Depends(get_db),
    _:  str     = Depends(get_api_key),
):
    return evaluation_service.get_evaluations_by_candidate(db, candidate_id)


@router.put("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
def update_evaluation(
    evaluation_id: int,
    payload: EvaluationUpdate,
    db: Session = Depends(get_db),
    _:  str     = Depends(get_api_key),
):
    return evaluation_service.update_evaluation(db, evaluation_id, payload)


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    _:  str     = Depends(get_api_key),
):
    return evaluation_service.get_evaluation_by_id(db, evaluation_id)
