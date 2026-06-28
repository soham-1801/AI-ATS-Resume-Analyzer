from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.ats_result import ATSResult
from app.schemas.ats_schema import DashboardStats
from app.schemas.dashboard_schema import DashboardAnalyticsResponse
from app.api.auth import get_current_user
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch basic candidate metrics and recent activity logs. Protected by JWT."""
    # Count scoped to the current user
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    total_matches = db.query(ATSResult).join(Resume).filter(Resume.user_id == current_user.id).count()
    
    avg_score_query = db.query(func.avg(ATSResult.ats_score)).join(Resume).filter(Resume.user_id == current_user.id).scalar()
    average_score = round(avg_score_query, 1) if avg_score_query is not None else 0.0

    recent_db_results = db.query(ATSResult).join(Resume)\
        .filter(Resume.user_id == current_user.id)\
        .order_by(ATSResult.created_at.desc()).limit(5).all()
    
    return DashboardStats(
        total_resumes=total_resumes,
        total_matches=total_matches,
        average_score=average_score,
        recent_matches=recent_db_results
    )

@router.get("/analytics", response_model=DashboardAnalyticsResponse, status_code=status.HTTP_200_OK)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch comprehensive aggregate statistics and charts-ready distribution data
    for the candidate. Protected by JWT.
    """
    return AnalyticsService.get_user_analytics(db, current_user.id)
