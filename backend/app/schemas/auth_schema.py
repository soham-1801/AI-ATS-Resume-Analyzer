from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class RefreshRequest(BaseModel):
    refresh_token: str

class OAuthLoginRequest(BaseModel):
    provider: Literal["google", "github"]
    oauth_id: str = Field(..., min_length=1)
    email: EmailStr
    name: str

class OAuthCodeExchangeRequest(BaseModel):
    code: str = Field(..., min_length=1)
    redirect_uri: str | None = None
    id_token: str | None = None
