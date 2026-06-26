from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class ATSResult(Base):
    __tablename__ = "ats_results"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    ats_score = Column(Float, nullable=False)
    matched_skills = Column(Text, nullable=True)  # JSON-encoded string or text block
    missing_skills = Column(Text, nullable=True)  # JSON-encoded string or text block
    suggestions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="ats_results")
    job_description = relationship("JobDescription", back_populates="ats_results")
