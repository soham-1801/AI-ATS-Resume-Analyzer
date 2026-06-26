from pydantic import BaseModel
from datetime import datetime

class JobDescriptionBase(BaseModel):
    description: str

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionResponse(JobDescriptionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
