import os
import uuid
import logging
from fastapi import UploadFile, HTTPException, status
from datetime import datetime, timezone

# Configure logger
logger = logging.getLogger("ats.file_service")

# Root directories configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "resumes")

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 Megabytes

class FileService:
    @staticmethod
    def validate_file(file: UploadFile):
        """Validate file format, mime type, and file size limits."""
        # 1. Validate File Format
        if not file.filename:
            logger.error("[UPLOAD VALIDATION] Filename is missing.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is missing."
            )
            
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            err_msg = "Unsupported file type. Only PDF, DOC, and DOCX files are allowed."
            logger.error(f"[UPLOAD VALIDATION] File '{file.filename}' extension '{ext}' not allowed. {err_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg
            )

        # 2. Validate MIME Type
        if file.content_type not in ALLOWED_MIME_TYPES:
            err_msg = f"Unsupported file type. MIME type '{file.content_type}' is not allowed."
            logger.error(f"[UPLOAD VALIDATION] File '{file.filename}' MIME type '{file.content_type}' not allowed. {err_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg
            )

        # 3. Validate File Size
        # Seek end of file to read length, then reset cursor position
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > MAX_FILE_SIZE_BYTES:
            err_msg = "File exceeds maximum allowed size of 5MB."
            logger.error(f"[UPLOAD VALIDATION] File '{file.filename}' size ({size} bytes) exceeds limit. {err_msg}")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=err_msg
            )

    @classmethod
    def save_file(cls, file: UploadFile) -> tuple[str, str]:
        """
        Validate and save an uploaded file to the local directory.
        Returns a tuple of (unique_filename, physical_file_path).
        """
        # Validate file
        cls.validate_file(file)
        
        # Ensure target folder exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Clean and create a secure, unique filename
        ext = file.filename.rsplit(".", 1)[-1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file to uploads/resumes/
        try:
            with open(file_path, "wb") as f:
                content = file.file.read()
                f.write(content)
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to write file to storage: {str(e)}"
            )
            
        return unique_filename, file_path
