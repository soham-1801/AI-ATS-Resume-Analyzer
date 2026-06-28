from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    name: str
    oauth_provider: str | None = None
    oauth_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
