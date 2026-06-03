from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
from app.database.session import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id     = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    communication    = Column(Float, nullable=False)
    technical        = Column(Float, nullable=False)
    problem_solving  = Column(Float, nullable=False)
    ownership        = Column(Float, nullable=False)
    final_score      = Column(Float, nullable=False, default=0.0, index=True)
    comments         = Column(Text, nullable=True)
    interviewer_name = Column(String(255), nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("communication >= 0 AND communication <= 10",    name="chk_communication"),
        CheckConstraint("technical >= 0 AND technical <= 10",            name="chk_technical"),
        CheckConstraint("problem_solving >= 0 AND problem_solving <= 10",name="chk_problem_solving"),
        CheckConstraint("ownership >= 0 AND ownership <= 10",            name="chk_ownership"),
    )

    candidate = relationship("Candidate", back_populates="evaluations")

    def calculate_final_score(self) -> float:
        return round(
            self.technical * 0.30
            + self.problem_solving * 0.25
            + self.communication * 0.20
            + self.ownership * 0.25,
            2,
        )
