import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.database.session import Base, get_db
from app.config import settings

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client  = TestClient(app)
HEADERS = {"X-API-Key": settings.API_KEY}


# Candidates

def test_create_candidate():
    resp = client.post("/candidates", json={
        "name": "Biplaba Kumar Samal", "email": "biplaba@example.com",
        "role": "Junior System Engineer", "experience": 2,
    }, headers=HEADERS)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Biplaba Kumar Samal"


def test_duplicate_email_rejected():
    resp = client.post("/candidates", json={
        "name": "Copy", "email": "biplaba@example.com",
        "role": "Engineer", "experience": 1,
    }, headers=HEADERS)
    assert resp.status_code == 409


def test_invalid_email_rejected():
    resp = client.post("/candidates", json={
        "name": "Test", "email": "not-an-email", "role": "Dev", "experience": 0,
    }, headers=HEADERS)
    assert resp.status_code == 422


def test_negative_experience_rejected():
    resp = client.post("/candidates", json={
        "name": "Test", "email": "neg@example.com", "role": "Dev", "experience": -1,
    }, headers=HEADERS)
    assert resp.status_code == 422


def test_list_candidates():
    resp = client.get("/candidates", headers=HEADERS)
    assert resp.status_code == 200
    assert "items" in resp.json()


def test_get_candidate():
    resp = client.get("/candidates/1", headers=HEADERS)
    assert resp.status_code == 200


def test_get_candidate_not_found():
    resp = client.get("/candidates/99999", headers=HEADERS)
    assert resp.status_code == 404


def test_update_candidate():
    resp = client.put("/candidates/1", json={"experience": 5}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["experience"] == 5


def test_filter_by_role():
    resp = client.get("/candidates?role=Junior", headers=HEADERS)
    assert resp.status_code == 200


# Evaluations

def test_create_evaluation():
    resp = client.post("/evaluations", json={
        "candidate_id": 1, "communication": 8,
        "technical": 9, "problem_solving": 7, "ownership": 8,
        "comments": "Solid candidate.", "interviewer_name": "John Doe",
    }, headers=HEADERS)
    assert resp.status_code == 201
    assert resp.json()["final_score"] == round(9*0.30 + 7*0.25 + 8*0.20 + 8*0.25, 2)


def test_score_formula():
    resp = client.post("/evaluations", json={
        "candidate_id": 1, "technical": 9,
        "problem_solving": 7, "communication": 8, "ownership": 8,
    }, headers=HEADERS)
    assert resp.status_code == 201
    expected = round(9*0.30 + 7*0.25 + 8*0.20 + 8*0.25, 2)
    assert resp.json()["final_score"] == expected


def test_score_out_of_range():
    resp = client.post("/evaluations", json={
        "candidate_id": 1, "communication": 11,
        "technical": 9, "problem_solving": 7, "ownership": 8,
    }, headers=HEADERS)
    assert resp.status_code == 422


def test_get_evaluations_for_candidate():
    resp = client.get("/candidates/1/evaluations", headers=HEADERS)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_evaluations_candidate_not_found():
    resp = client.get("/candidates/99999/evaluations", headers=HEADERS)
    assert resp.status_code == 404


# Rankings

def test_rankings_sorted_descending():
    resp = client.get("/candidates/rankings", headers=HEADERS)
    assert resp.status_code == 200
    scores = [r["avg_final_score"] for r in resp.json() if r["avg_final_score"] is not None]
    assert scores == sorted(scores, reverse=True)


# Auth

def test_missing_api_key():
    assert client.get("/candidates").status_code == 401


def test_invalid_api_key():
    assert client.get("/candidates", headers={"X-API-Key": "wrong"}).status_code == 401


# Health

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
