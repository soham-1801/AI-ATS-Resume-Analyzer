from pydantic import BaseModel
from datetime import datetime

class ResumeBase(BaseModel):
    file_name: str

class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    file_path: str
    upload_date: datetime
    parsed_text: str | None = None

    class Config:
        from_attributes = True

class ResumeParseDetails(BaseModel):
    resume_id: int
    parsed_text: str
    extracted_skills: list[str]
