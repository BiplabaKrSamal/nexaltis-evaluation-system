from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database.session import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(255), nullable=False, index=True)
    email      = Column(String(255), nullable=False, unique=True, index=True)
    role       = Column(String(255), nullable=False, index=True)
    experience = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    evaluations = relationship("Evaluation", back_populates="candidate", cascade="all, delete-orphan")
