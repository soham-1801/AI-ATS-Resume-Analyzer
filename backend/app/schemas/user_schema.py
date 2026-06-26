from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    name: str
    password: str

class UserResponse(UserBase):
    id: int
    name: str
    oauth_provider: str | None = None
    oauth_id: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
