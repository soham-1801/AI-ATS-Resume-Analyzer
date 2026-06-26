import os
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume_schema import ResumeResponse
from app.api.auth import get_current_user
from app.services.file_service import FileService
from app.services.resume_parser import ResumeParser

# Configure logger
logger = logging.getLogger("ats.resume")

router = APIRouter(prefix="/resume", tags=["Resumes"])

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a resume (PDF/DOCX), validate size/format, save to disk and DB, 
    and extract text contents. Protected by JWT auth.
    """
    print(f"[RESUME UPLOAD] Received file upload request. Filename: {file.filename}, User: {current_user.email}")
    
    file_path = None
    try:
        # 1. Save file to uploads/resumes/ using FileService (performs validation)
        unique_filename, file_path = FileService.save_file(file)
        print(f"[RESUME UPLOAD] File successfully saved to local directory: {file_path}")
     
        # 2. Extract text from the saved file using ResumeParser
        parsed_text = ResumeParser.parse(file_path)
        text_length = len(parsed_text) if parsed_text else 0
        print(f"[RESUME UPLOAD] Extracted text length: {text_length} characters")
        
        if not parsed_text or not parsed_text.strip() or text_length < 20:
            raise ValueError("Empty document: The file contains no readable text content or is too short (minimum 20 characters).")
            
    except HTTPException as he:
        # Clean up file if it was somehow written
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        print(f"[RESUME UPLOAD] Validation failure for {file.filename}: {he.detail}")
        logger.error(f"[RESUME UPLOAD] Validation failure for {file.filename}: {he.detail}")
        raise he
        
    except Exception as e:
        # Cleanup uploaded file if parsing fails
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_err:
                print(f"[RESUME UPLOAD] Error cleaning up file: {cleanup_err}")
                
        error_msg = str(e)
        # Check if it's a known error prefix or make it friendly
        if "Unsupported file type:" in error_msg:
            detail_msg = error_msg
        elif "Corrupted document:" in error_msg:
            detail_msg = error_msg
        elif "Empty document:" in error_msg:
            detail_msg = error_msg
        else:
            detail_msg = f"Corrupted document: Failed to parse resume text contents. Details: {error_msg}"
            
        print(f"[RESUME UPLOAD] Error during text parsing: {detail_msg}")
        logger.error(f"[RESUME UPLOAD] Parsing failure for {file.filename}: {detail_msg}")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_msg
        )

    # 3. Save Resume record in database
    db_resume = Resume(
        user_id=current_user.id,
        file_name=unique_filename,
        file_path=file_path,
        parsed_text=parsed_text
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    return db_resume

@router.get("/all", response_model=list[ResumeResponse])
def get_all_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all resumes uploaded by the current authenticated user."""
    return db.query(Resume).filter(Resume.user_id == current_user.id).all()

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details of a specific resume belonging to the logged-in user."""
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied."
        )
    return resume

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume record and its local physical file."""
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied."
        )
        
    # Delete physical file from storage
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            print(f"Error removing file from storage: {e}")
            
    db.delete(resume)
    db.commit()
    return
