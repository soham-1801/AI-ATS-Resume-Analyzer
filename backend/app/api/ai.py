from fastapi import APIRouter, Depends, status
from app.schemas.ai_schema import AIAnalyzeRequest, AIAnalyzeResponse, AIRewriteRequest, AIRewriteResponse
from app.services.ai_suggestions import AISuggestions
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["AI Suggestions"])

@router.post("/analyze", response_model=AIAnalyzeResponse, status_code=status.HTTP_200_OK)
def analyze_resume_improvements(
    request: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed AI-driven optimization suggestions to improve a candidate's resume score.
    Powered by Gemini 1.5 Flash. Protected by JWT.
    """
    suggestions = AISuggestions.generate_gemini_suggestions(
        resume_text=request.resume_text,
        job_description=request.job_description,
        ats_score=request.ats_score,
        matched_skills=request.matched_skills,
        missing_skills=request.missing_skills
    )
    
    return AIAnalyzeResponse(
        summary_improvement=suggestions.get("summary_improvement", ""),
        missing_keywords=suggestions.get("missing_keywords", []),
        project_suggestions=suggestions.get("project_suggestions", []),
        experience_suggestions=suggestions.get("experience_suggestions", []),
        ats_tips=suggestions.get("ats_tips", [])
    )

@router.post("/rewrite", response_model=AIRewriteResponse, status_code=status.HTTP_200_OK)
def rewrite_resume_section(
    request: AIRewriteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Rewrite a resume section (summary, experience, project, or skills) to be highly polished
    and metrics-oriented using Gemini 1.5 Flash. Protected by JWT.
    """
    improved_content = AISuggestions.rewrite_resume_section(
        section=request.section,
        content=request.content
    )
    
    return AIRewriteResponse(
        improved_content=improved_content
    )

