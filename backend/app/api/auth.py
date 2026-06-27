from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
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

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2PasswordBearer for extracting the token from authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency to get the currently authenticated user from a JWT token."""
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
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Endpoint to register a new candidate user."""
    return AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Endpoint to authenticate user and retrieve JWT access token and refresh token."""
    user = AuthService.authenticate_user(db, user_data)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token and refresh token."""
    payload = decode_refresh_token(request.refresh_token)
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
def oauth_login(request: OAuthLoginRequest, db: Session = Depends(get_db)):
    """Endpoint for Google, GitHub, or Apple Social Login."""
    if not request.provider or not str(request.provider).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="provider is required")
    if request.provider not in ("google", "github", "apple"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth provider")
    if not request.oauth_id or not str(request.oauth_id).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="oauth_id is required")

    user = AuthService.authenticate_or_create_oauth_user(db, request)
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

def validate_redirect_uri(uri: str | None):
    if uri:
        parsed = urlparse(uri)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid redirect_uri")

@router.post("/oauth/google", response_model=Token)
def oauth_google_login(request: OAuthCodeExchangeRequest, db: Session = Depends(get_db)):
    """Exchange Google auth code for a valid access/refresh JWT token."""
    if not request.code or not str(request.code).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="code is required")
    if not request.redirect_uri or not str(request.redirect_uri).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="redirect_uri is required")
    validate_redirect_uri(request.redirect_uri)
    profile = OAuthService.exchange_google_code(request.code, request.redirect_uri)
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
def oauth_github_login(request: OAuthCodeExchangeRequest, db: Session = Depends(get_db)):
    """Exchange GitHub auth code for a valid access/refresh JWT token."""
    if not request.code or not str(request.code).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="code is required")
    validate_redirect_uri(request.redirect_uri)
    profile = OAuthService.exchange_github_code(request.code, request.redirect_uri)
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

@router.post("/oauth/apple", response_model=Token)
def oauth_apple_login(request: OAuthCodeExchangeRequest, db: Session = Depends(get_db)):
    """Validate Apple ID token and exchange for access/refresh JWT token."""
    # Frontends send id_token, and optionally code
    id_token = request.id_token or request.code
    if not id_token or not str(id_token).strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id_token or code is required")
    profile = OAuthService.verify_apple_token(id_token, request.code)
    oauth_request = OAuthLoginRequest(
        provider="apple",
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

class ResetPasswordRequestRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirmRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
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
def reset_password_request(
    request_data: ResetPasswordRequestRequest,
    db: Session = Depends(get_db)
):
    """Endpoint to request a password reset token."""
    token = AuthService.request_password_reset(db, request_data.email)
    return {
        "message": "If this email is registered, a reset code has been sent."
    }

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    request_data: ResetPasswordConfirmRequest,
    db: Session = Depends(get_db)
):
    """Endpoint to reset password using a reset token."""
    AuthService.confirm_password_reset(db, request_data.email, request_data.token, request_data.new_password)
    return {"message": "Password has been reset successfully."}
