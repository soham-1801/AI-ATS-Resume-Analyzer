from pydantic import BaseModel
from datetime import datetime

class ATSAnalyzeRequest(BaseModel):
    resume_id: int
    job_description_id: int

class CategoryBreakdownItem(BaseModel):
    name: str
    score: float
    deduction_reason: str
    missing_elements: list[str]
    recommendations: list[str]
    potential_gain: float
    calculation_reason: str
    why_this_score: str = ""
    issues: list[str] = []
    target_score: float = 80.0
    improvement_needed: float = 0.0

class PriorityFix(BaseModel):
    title: str
    impact: str
    description: str
    points_recovery: float

class MissingSkillImpactItem(BaseModel):
    skill: str
    impact: float

class ATSIntelligence(BaseModel):
    grade: str
    readiness_indicator: str
    hiring_probability: str
    current_score: float
    recoverable_score: float
    max_score: float
    projected_score: float
    keyword_impact_score: float
    strengths: list[str]
    weaknesses: list[str]
    priority_fixes: list[PriorityFix]
    found_sections: list[str] = []
    missing_sections: list[str] = []
    required_keywords: list[str] = []
    found_keywords: list[str] = []
    keyword_coverage_percentage: float = 0.0
    missing_keywords: list[str] = []
    compatibility_recovery: float = 0.0
    improvement_summary: list[str] = []
    missing_skills_impact: list[MissingSkillImpactItem] = []
    total_skills_impact_gain: float = 0.0

class ATSAnalyzeResponse(BaseModel):
    id: int | None = None
    keyword_score: float
    semantic_score: float
    final_score: float
    ats_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    match_percentage: float
    suggestions: str | None = None
    category_breakdown: list[CategoryBreakdownItem]
    improvement_roadmap: list[str]
    keywords_impact_analysis: str
    skill_validation_explanation: str
    estimated_future_score: str
    intelligence_layer: ATSIntelligence

class ATSRequest(BaseModel):
    resume_id: int
    jd_id: int

class ATSResultResponse(BaseModel):
    id: int
    resume_id: int
    jd_id: int
    ats_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    suggestions: str | None
    created_at: datetime

    class Config:
        from_attributes = True
        
class DashboardStats(BaseModel):
    total_resumes: int
    total_matches: int
    average_score: float
    recent_matches: list[ATSResultResponse]
