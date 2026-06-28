from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class JobDescriptionBase(BaseModel):
    description: str = Field(..., min_length=10)

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionResponse(JobDescriptionBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
