import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.ats_result import ATSResult
from app.schemas.ats_schema import ATSAnalyzeRequest, ATSAnalyzeResponse
from app.api.auth import get_current_user
from app.services.ats_engine import ATSEngine
from app.services.ai_suggestions import AISuggestions
from app.services.pdf_generator import PDFGenerator
from app.services.resume_parser import ResumeParser

logger = logging.getLogger("ats.api.ats")

router = APIRouter(prefix="/ats", tags=["ATS Analysis"])


@router.post("/analyze", response_model=ATSAnalyzeResponse,
             status_code=status.HTTP_201_CREATED)
def analyze_resume(
    request: ATSAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform deep ATS comparison between a resume and a job description.
    Saves the audit result in the database and returns score and skill match details.
    Protected by JWT.
    """
    # Debug payload logging
    payload_dict = {"resume_id": request.resume_id,
                    "job_description_id": request.job_description_id}
    print(
        f"[ATS ANALYSIS] Request received. Payload: {payload_dict}, User: {
            current_user.email}")
    print(f"[ATS ANALYSIS] Selected Resume ID: {request.resume_id}")

    # 1. Load resume and check permissions
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id).first()
    if not resume:
        print(
            f"[ATS ANALYSIS] Error: Resume ID {
                request.resume_id} not found or access denied.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied."
        )

    # 2. Check if text is present. If missing, attempt automatic re-parsing
    if not resume.parsed_text or not resume.parsed_text.strip():
        print(
            f"[ATS ANALYSIS] Warning: Resume {
                resume.id} parsed_text is empty. Attempting automatic re-parsing from path: {
                resume.file_path}")
        try:
            parsed_text = ResumeParser.parse(resume.file_path)
            if parsed_text and parsed_text.strip():
                resume.parsed_text = parsed_text
                db.commit()
                db.refresh(resume)
                print(
                    f"[ATS ANALYSIS] Success: Automatically re-parsed resume {
                        resume.id}. Length: {
                        len(parsed_text)} characters.")
            else:
                raise ValueError(
                    "Parsed file has no extractable text. It may be empty or a scanned PDF (image-only).")
        except Exception as e:
            print(
                f"[ATS ANALYSIS] Automatic re-parsing failed for Resume {resume.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resume text has not been parsed or is empty. Scanned PDFs are not supported. Error: {
                    str(e)}")

    # 2. Load job description and check permissions
    jd = db.query(JobDescription).filter(
        JobDescription.id == request.job_description_id,
        JobDescription.user_id == current_user.id).first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found or access denied."
        )

    if not jd.description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is empty."
        )

    # Log extracted character count before ATS analysis
    char_count = len(resume.parsed_text) if resume.parsed_text else 0
    print(
        f"[ATS ANALYSIS] Starting ATS analysis. Resume character count: {char_count}")
    logger.info(
        f"[ATS ANALYSIS] Starting ATS analysis for Resume ID {
            resume.id}. Extracted resume character count: {char_count}")

    # 3. Calculate match metrics using ATSEngine
    match_data = ATSEngine.calculate_match(resume.parsed_text, jd.description)

    keyword_score = match_data["keyword_score"]
    semantic_score = match_data["semantic_score"]
    final_score = match_data["final_score"]
    ats_score = match_data["ats_score"]
    matched_skills = match_data["matched_skills"]
    missing_skills = match_data["missing_skills"]
    match_percentage = match_data["match_percentage"]

    # 4. Generate suggestions for record auditing
    suggestions = AISuggestions.generate_suggestions(
        resume_text=resume.parsed_text,
        job_description=jd.description,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        score=final_score
    )

    # 5. Store result in ATSResult database table
    db_result = ATSResult(
        resume_id=request.resume_id,
        jd_id=request.job_description_id,
        ats_score=final_score,
        matched_skills=json.dumps(matched_skills),
        missing_skills=json.dumps(missing_skills),
        suggestions=suggestions
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    # 6. Return response according to specifications
    return ATSAnalyzeResponse(
        id=db_result.id,
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        final_score=final_score,
        ats_score=ats_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        match_percentage=match_percentage,
        suggestions=suggestions,
        category_breakdown=match_data.get(
            "category_breakdown",
            []),
        improvement_roadmap=match_data.get(
            "improvement_roadmap",
            []),
        keywords_impact_analysis=match_data.get(
            "keywords_impact_analysis",
            ""),
        skill_validation_explanation=match_data.get(
            "skill_validation_explanation",
            ""),
        estimated_future_score=match_data.get(
            "estimated_future_score",
            ""),
        intelligence_layer=match_data.get(
            "intelligence_layer",
            {}))


@router.get("/results/{resume_id}", status_code=status.HTTP_200_OK)
def get_ats_results_for_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all past ATS comparison results for a specific resume belonging to the user."""
    # Verify candidate ownership of resume first
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied."
        )

    db_results = db.query(ATSResult).filter(
        ATSResult.resume_id == resume_id).all()

    parsed_results = []
    for result in db_results:
        try:
            m_skills = json.loads(
                result.matched_skills) if result.matched_skills else []
        except Exception:
            m_skills = []
        try:
            ms_skills = json.loads(
                result.missing_skills) if result.missing_skills else []
        except Exception:
            ms_skills = []

        parsed_results.append({
            "id": result.id,
            "resume_id": result.resume_id,
            "jd_id": result.jd_id,
            "ats_score": result.ats_score,
            "matched_skills": m_skills,
            "missing_skills": ms_skills,
            "suggestions": result.suggestions,
            "created_at": result.created_at
        })
    return parsed_results


@router.get("/results/{result_id}/pdf")
def get_pdf_report(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and stream a professional PDF evaluation report for a given ATS audit ID.
    Protected by JWT.
    """
    print(
        f"[PDF REPORT] Request received for result ID: {result_id}. User: {
            current_user.email}")

    # 1. Fetch the ATSResult record
    result = db.query(ATSResult).filter(ATSResult.id == result_id).first()
    if not result:
        print(
            f"[PDF REPORT] Error: ATS result record ID {result_id} not found in database.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ATS analysis result not found."
        )

    # 2. Verify resume ownership
    resume = db.query(Resume).filter(
        Resume.id == result.resume_id,
        Resume.user_id == current_user.id).first()
    if not resume:
        print(
            f"[PDF REPORT] Access Denied: User {
                current_user.email} does not own resume ID {
                result.resume_id} linked to result ID {result_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied or resume not owned by current user."
        )

    # 3. Load Job Description
    jd = db.query(JobDescription).filter(
        JobDescription.id == result.jd_id).first()
    jd_desc = jd.description if jd else ""
    print(
        f"[PDF REPORT] Loaded Job Description ID: {
            result.jd_id if jd else 'N/A'}")

    # 4. Compute scores dynamically using ATSEngine to retrieve Keyword and
    # Semantic scores
    try:
        match_data = ATSEngine.calculate_match(resume.parsed_text, jd_desc)
    except Exception as match_err:
        print(
            f"[PDF REPORT] Error calculating match scores dynamically: {match_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate match metrics: {str(match_err)}"
        )

    # 5. Extract skills lists
    try:
        m_skills = json.loads(
            result.matched_skills) if result.matched_skills else []
    except Exception:
        m_skills = []
    try:
        ms_skills = json.loads(
            result.missing_skills) if result.missing_skills else []
    except Exception:
        ms_skills = []

    print(
        f"[PDF REPORT] Generating PDF byte stream. Candidate: {
            current_user.name}, Keyword Score: {
            match_data.get('keyword_score')}, Semantic Score: {
                match_data.get('semantic_score')}, Final Score: {
                    result.ats_score}")

    # 6. Generate PDF byte stream
    try:
        pdf_buffer = PDFGenerator.generate_report(
            candidate_name=current_user.name,
            candidate_email=current_user.email,
            job_title="Target Position Specification" if not jd else f"Target Job Profile (ID: {
                jd.id})",
            upload_date=result.created_at,
            keyword_score=match_data.get(
                "keyword_score",
                0.0),
            semantic_score=match_data.get(
                "semantic_score",
                0.0),
            final_score=result.ats_score,
            matched_skills=m_skills,
            missing_skills=ms_skills,
            suggestions=result.suggestions,
            category_breakdown=match_data.get(
                "category_breakdown",
                []),
            intelligence_layer=match_data.get(
                "intelligence_layer",
                {}),
            improvement_roadmap=match_data.get(
                "improvement_roadmap",
                []),
            keywords_impact_analysis=match_data.get(
                "keywords_impact_analysis",
                ""),
            skill_validation_explanation=match_data.get(
                "skill_validation_explanation",
                ""),
            estimated_future_score=match_data.get(
                "estimated_future_score",
                ""))
    except Exception as pdf_err:
        print(f"[PDF REPORT] Error generating PDF report: {pdf_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF document: {str(pdf_err)}"
        )

    clean_filename = f"ATS_Report_Result_{result.id}.pdf"
    print(
        f"[PDF REPORT] PDF generated successfully. Streaming file to user as: {clean_filename}")

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={clean_filename}"})
