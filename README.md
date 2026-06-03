# NexAltis Candidate Evaluation System

Backend API for managing candidates, recording interview evaluations, and ranking applicants by weighted score.

Built with FastAPI, PostgreSQL, SQLAlchemy, and Pydantic v2.

---

## Tech stack

| Layer      | Technology         |
|------------|--------------------|
| Framework  | FastAPI 0.111      |
| Language   | Python 3.11        |
| ORM        | SQLAlchemy 2.0     |
| Database   | PostgreSQL 15      |
| Validation | Pydantic v2        |
| Auth       | API Key header     |
| Containers | Docker + Compose   |

---

## Getting started

### Docker (recommended)

```bash
docker-compose up --build
```

API available at `http://localhost:8000`. Swagger docs at `/docs`.

### Local setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # update DATABASE_URL

psql -U postgres -c "CREATE DATABASE nexaltis_db;"

python seed.py              # load sample data
uvicorn main:app --reload
```

---

## Authentication

All endpoints require an API key:

```
X-API-Key: nexaltis-api-key-2026
```

Set a different key in `.env` before deploying.

---

## API endpoints

### Candidates

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/candidates` | Create candidate |
| GET | `/candidates` | List candidates (paginated, role filter) |
| GET | `/candidates/{id}` | Get by ID |
| PUT | `/candidates/{id}` | Update |
| DELETE | `/candidates/{id}` | Delete (cascades evaluations) |
| GET | `/candidates/rankings` | Ranked by avg score |
| GET | `/candidates/{id}/evaluations` | Candidate's evaluations |

### Evaluations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/evaluations` | Submit evaluation (auto-scores) |
| GET | `/evaluations/{id}` | Get by ID |
| PUT | `/evaluations/{id}` | Update (recalculates score) |

### Filtering & pagination

```
GET /candidates?role=System Engineer&page=1&page_size=10
```

---

## Scoring formula

```
Final Score = (Technical × 0.30) + (Problem Solving × 0.25) + (Communication × 0.20) + (Ownership × 0.25)
```

Scores are calculated and stored automatically on create and recalculated on update. Rankings use the average across all evaluations per candidate.

---

## Database schema

```
candidates
  id, name, email (unique), role, experience, created_at, updated_at

evaluations
  id, candidate_id (FK → candidates.id CASCADE), communication, technical,
  problem_solving, ownership, final_score, comments, interviewer_name,
  created_at, updated_at
```

---

## Running tests

```bash
pytest tests/ -v
```

Uses SQLite in-memory — no PostgreSQL needed for tests.

---

## Project structure

```
nexaltis/
├── main.py
├── seed.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── alembic/
│   └── versions/001_initial_schema.py
└── app/
    ├── config.py
    ├── auth.py
    ├── database/session.py
    ├── models/
    │   ├── candidate.py
    │   └── evaluation.py
    ├── schemas/
    │   ├── candidate.py
    │   ├── evaluation.py
    │   └── common.py
    ├── routes/
    │   ├── candidates.py
    │   └── evaluations.py
    └── services/
        ├── candidate_service.py
        └── evaluation_service.py
```

---

## Design decisions

- `final_score` is stored in the DB rather than computed on read — keeps ranking queries fast
- Rankings use `AVG(final_score)` across all evaluations per candidate so multiple interview rounds are factored in
- DB-level `CHECK` constraints enforce score range (0–10) as a safety net below the API layer
- Cascade delete on evaluations keeps referential integrity without manual cleanup
- Partial updates via `model_dump(exclude_unset=True)` so callers only send changed fields
