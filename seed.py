from app.database.session import SessionLocal, init_db
from app.models.candidate import Candidate
from app.models.evaluation import Evaluation

init_db()

CANDIDATES = [
    {"name": "Arjun Mehta",  "email": "arjun@example.com",  "role": "Backend Engineer",       "experience": 4},
    {"name": "Priya Sharma", "email": "priya@example.com",  "role": "Full Stack Developer",   "experience": 3},
    {"name": "Rahul Nair",   "email": "rahul@example.com",  "role": "Junior System Engineer", "experience": 1},
    {"name": "Sneha Iyer",   "email": "sneha@example.com",  "role": "AI/ML Engineer",         "experience": 2},
    {"name": "Vikram Bose",  "email": "vikram@example.com", "role": "DevOps Engineer",        "experience": 5},
    {"name": "Anika Das",    "email": "anika@example.com",  "role": "Full Stack Developer",   "experience": 2},
]

# (candidate_index, technical, problem_solving, communication, ownership, comment, interviewer)
EVALUATIONS = [
    (0, 8, 7, 8, 8, "Strong backend fundamentals, good system design instincts.", "Jane Smith"),
    (1, 9, 9, 9, 9, "Exceptional all-round. Highest scorer this cycle.",          "John Doe"),
    (2, 6, 6, 7, 7, "Good potential, needs mentoring on advanced topics.",        "Jane Smith"),
    (3, 9, 8, 9, 9, "Outstanding ML depth. Best AI candidate we've seen.",       "John Doe"),
    (4, 8, 8, 7, 8, "Solid DevOps, impressive CI/CD knowledge.",                 "Jane Smith"),
    (0, 9, 8, 8, 7, "Round 2 — significant improvement from first interview.",   "Mike Lee"),
    (1, 8, 9, 8, 8, "Consistent across rounds. Recommend for offer.",            "Mike Lee"),
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Candidate).count() > 0:
            print("Already seeded, skipping.")
            return

        ids = []
        for data in CANDIDATES:
            c = Candidate(**data)
            db.add(c)
            db.commit()
            db.refresh(c)
            ids.append(c.id)
            print(f"  + {c.name}")

        for ci, tech, ps, comm, own, comment, iname in EVALUATIONS:
            e = Evaluation(
                candidate_id=ids[ci],
                technical=tech, problem_solving=ps,
                communication=comm, ownership=own,
                comments=comment, interviewer_name=iname,
            )
            e.final_score = round(tech * 0.30 + ps * 0.25 + comm * 0.20 + own * 0.25, 2)
            db.add(e)

        db.commit()
        print(f"\nSeeded {len(CANDIDATES)} candidates, {len(EVALUATIONS)} evaluations.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
