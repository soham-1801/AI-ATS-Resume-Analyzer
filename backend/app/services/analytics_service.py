import json
from collections import Counter
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.models.ats_result import ATSResult
from app.models.job_description import JobDescription
from app.schemas.dashboard_schema import DashboardAnalyticsResponse, SkillFrequency, ScoreHistoryItem, ScoreDistribution

logger = logging.getLogger(__name__)

class AnalyticsService:
    @staticmethod
    def get_user_analytics(db: Session, user_id: int) -> DashboardAnalyticsResponse:
        """
        Gathers dashboard analytics metrics and charts-ready aggregates 
        for a specific candidate user.
        """
        # 1. Total resumes uploaded by user
        total_resumes = db.query(Resume).filter(Resume.user_id == user_id).count()

        # 2. Total analyses performed on user's resumes
        analyses_query = db.query(ATSResult).join(Resume).filter(Resume.user_id == user_id)
        total_analyses = analyses_query.count()

        # 3. Calculate score metrics (avg, highest, lowest)
        score_stats = db.query(
            func.avg(ATSResult.ats_score),
            func.max(ATSResult.ats_score),
            func.min(ATSResult.ats_score)
        ).join(Resume).filter(Resume.user_id == user_id).first()

        if score_stats:
            avg_score = round(score_stats[0], 1) if score_stats[0] is not None else 0.0
            highest_score = round(score_stats[1], 1) if score_stats[1] is not None else 0.0
            lowest_score = round(score_stats[2], 1) if score_stats[2] is not None else 0.0
        else:
            avg_score = highest_score = lowest_score = 0.0

        # 4. Aggregate Top Skills matched across all analyses
        matched_results = db.query(ATSResult.matched_skills).join(Resume).filter(Resume.user_id == user_id).all()
        
        skill_counter = Counter()
        for row in matched_results:
            if row[0]:
                try:
                    skills_list = json.loads(row[0])
                    if isinstance(skills_list, list):
                        skill_counter.update(skills_list)
                except Exception as e:
                    logger.warning(f"Failed to parse skills JSON: {e}", exc_info=True)

        # Sort and select top 10 skills
        top_skills = [
            SkillFrequency(skill=skill, count=count)
            for skill, count in skill_counter.most_common(10)
        ]

        # 5. Compile Score Distribution ranges
        low_count = analyses_query.filter(ATSResult.ats_score < 50).count()
        med_count = analyses_query.filter(ATSResult.ats_score >= 50, ATSResult.ats_score < 75).count()
        high_count = analyses_query.filter(ATSResult.ats_score >= 75).count()

        distribution = ScoreDistribution(
            low=low_count,
            medium=med_count,
            high=high_count
        )

        # 6. Fetch last 10 analysis history items (for trends chart)
        history_records = db.query(
            ATSResult.ats_score,
            ATSResult.created_at,
            JobDescription.id.label("jd_id"),
            ATSResult.id.label("result_id")
        ).join(Resume, Resume.id == ATSResult.resume_id)\
         .outerjoin(JobDescription, JobDescription.id == ATSResult.jd_id)\
         .filter(Resume.user_id == user_id)\
         .order_by(ATSResult.created_at.asc())\
         .limit(10).all()

        score_history = []
        for record in history_records:
            date_str = record[1].strftime("%b %d") if record[1] else "Unknown"
            score_history.append(
                ScoreHistoryItem(
                    id=record[3],
                    date=date_str,
                    score=record[0],
                    job_title=f"Position ID: {record[2]}" if record[2] else "N/A"
                )
            )

        return DashboardAnalyticsResponse(
            total_resumes=total_resumes,
            total_analyses=total_analyses,
            average_ats_score=avg_score,
            highest_score=highest_score,
            lowest_score=lowest_score,
            top_skills=top_skills,
            score_history=score_history,
            score_distribution=distribution
        )
