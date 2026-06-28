from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.models.job_description import JobDescription
from app.schemas.job_description_schema import JobDescriptionCreate, JobDescriptionResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/job-description", tags=["Job Descriptions"])

@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(
    request: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job description. Protected by JWT."""
    db_jd = JobDescription(
        user_id=current_user.id,
        description=request.description
    )
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd

@router.get("/all", response_model=list[JobDescriptionResponse])
def get_all_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all job descriptions for the authenticated user."""
    return db.query(JobDescription).filter(JobDescription.user_id == current_user.id).all()

@router.get("/{jd_id}", response_model=JobDescriptionResponse)
def get_job_description(
    jd_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single job description by ID. Protected by JWT."""
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == current_user.id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found or access denied."
        )
    return jd

@router.delete("/{jd_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_description(
    jd_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job description. Protected by JWT."""
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == current_user.id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found or access denied."
        )
    db.delete(jd)
    db.commit()
    from fastapi import Response
    return Response(status_code=status.HTTP_204_NO_CONTENT)
