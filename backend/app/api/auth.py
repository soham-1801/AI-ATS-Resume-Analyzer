from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.auth_schema import UserLogin, Token, RefreshRequest, OAuthLoginRequest, OAuthCodeExchangeRequest
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService
from app.utils.security import create_access_token, decode_access_token, verify_password, get_password_hash, validate_password_strength, create_refresh_token, decode_refresh_token
from pydantic import BaseModel, EmailStr
from urllib.parse import urlparse
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

# HTTPBearer for extracting the Bearer token from the authorization header
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Dependency to get the currently authenticated user from a JWT token."""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
        
    user = AuthService.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Endpoint to register a new candidate user."""
    return AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Endpoint to authenticate user and retrieve JWT access token and refresh token."""
    user = AuthService.authenticate_user(db, user_data)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh_token(request: Request, req: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token and refresh token."""
    payload = decode_refresh_token(req.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )
    user = AuthService.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )
    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post("/oauth", response_model=Token)
@limiter.limit("5/minute")
def oauth_login(request: Request, req: OAuthLoginRequest, db: Session = Depends(get_db)):
    """Endpoint for Google or GitHub Social Login."""
    if not req.provider or not str(req.provider).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="provider is required")
    if req.provider not in ("google", "github"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth provider")
    if not req.oauth_id or not str(req.oauth_id).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="oauth_id is required")

    user = AuthService.authenticate_or_create_oauth_user(db, req)
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

def validate_redirect_uri(uri: str | None):
    if uri:
        parsed = urlparse(uri)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid redirect_uri")

@router.post("/oauth/google", response_model=Token)
@limiter.limit("5/minute")
def oauth_google_login(request: Request, req: OAuthCodeExchangeRequest, db: Session = Depends(get_db)):
    """Exchange Google auth code for a valid access/refresh JWT token."""
    if not req.code or not str(req.code).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="code is required")
    if not req.redirect_uri or not str(req.redirect_uri).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="redirect_uri is required")
    validate_redirect_uri(req.redirect_uri)
    profile = OAuthService.exchange_google_code(req.code, req.redirect_uri)
    oauth_request = OAuthLoginRequest(
        provider="google",
        oauth_id=profile["oauth_id"],
        email=profile["email"],
        name=profile["name"]
    )
    user = AuthService.authenticate_or_create_oauth_user(db, oauth_request)
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/oauth/github", response_model=Token)
@limiter.limit("5/minute")
def oauth_github_login(request: Request, req: OAuthCodeExchangeRequest, db: Session = Depends(get_db)):
    """Exchange GitHub auth code for a valid access/refresh JWT token."""
    if not req.code or not str(req.code).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="code is required")
    validate_redirect_uri(req.redirect_uri)
    profile = OAuthService.exchange_github_code(req.code, req.redirect_uri)
    oauth_request = OAuthLoginRequest(
        provider="github",
        oauth_id=profile["oauth_id"],
        email=profile["email"],
        name=profile["name"]
    )
    user = AuthService.authenticate_or_create_oauth_user(db, oauth_request)
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details of the currently logged-in user."""
    return current_user

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirmRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str

@router.post("/change-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
def change_password(
    request: Request,
    request_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint for a logged-in user to change their password."""
    # Verify old password
    if not verify_password(request_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password."
        )
        
    # Prevent reusing the same password
    if request_data.old_password == request_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the old password."
        )
    
    # Validate new password strength
    try:
        validate_password_strength(request_data.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    # Hash and save new password
    current_user.password_hash = get_password_hash(request_data.new_password)
    db.commit()
    return {"message": "Password changed successfully."}

@router.post("/reset-password-request", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
def reset_password_request(
    request: Request,
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Endpoint to request a password reset token."""
    AuthService.request_password_reset(db, request_data.email)
    return {
        "message": "If this email is registered, a reset code has been sent."
    }

@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def reset_password(
    request: Request,
    request_data: ResetPasswordConfirmRequest,
    db: Session = Depends(get_db)
):
    """Endpoint to reset password using a reset token."""
    AuthService.confirm_password_reset(db, request_data.email, request_data.token, request_data.new_password)
    return {"message": "Password has been reset successfully."}
