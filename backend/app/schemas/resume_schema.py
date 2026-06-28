from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ResumeBase(BaseModel):
    file_name: str = Field(..., min_length=1)

class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    file_path: str
    upload_date: datetime
    parsed_text: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ResumeParseDetails(BaseModel):
    resume_id: int
    parsed_text: str
    extracted_skills: list[str]
