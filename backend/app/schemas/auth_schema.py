from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class RefreshRequest(BaseModel):
    refresh_token: str

class OAuthLoginRequest(BaseModel):
    provider: str
    oauth_id: str
    email: EmailStr
    name: str

class OAuthCodeExchangeRequest(BaseModel):
    code: str
    redirect_uri: str | None = None
    id_token: str | None = None
