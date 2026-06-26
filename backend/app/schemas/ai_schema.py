from pydantic import BaseModel

class AIAnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str
    ats_score: float
    matched_skills: list[str]
    missing_skills: list[str]

class AIAnalyzeResponse(BaseModel):
    summary_improvement: str
    missing_keywords: list[str]
    project_suggestions: list[str]
    experience_suggestions: list[str]
    ats_tips: list[str]

class AIRewriteRequest(BaseModel):
    section: str
    content: str

class AIRewriteResponse(BaseModel):
    improved_content: str

