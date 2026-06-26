from pydantic import BaseModel
from datetime import datetime

class SkillFrequency(BaseModel):
    skill: str
    count: int

class ScoreHistoryItem(BaseModel):
    id: int
    date: str
    score: float
    job_title: str | None = None

class ScoreDistribution(BaseModel):
    low: int      # < 50
    medium: int   # 50 - 75
    high: int     # >= 75

class DashboardAnalyticsResponse(BaseModel):
    total_resumes: int
    total_analyses: int
    average_ats_score: float
    highest_score: float
    lowest_score: float
    top_skills: list[SkillFrequency]
    score_history: list[ScoreHistoryItem]
    score_distribution: ScoreDistribution
