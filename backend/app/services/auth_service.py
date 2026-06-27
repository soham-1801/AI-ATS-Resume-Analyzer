from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.schemas.user_schema import UserCreate
from app.schemas.auth_schema import UserLogin, OAuthLoginRequest
from app.utils.security import get_password_hash, verify_password, validate_password_strength
import secrets
import hashlib
from datetime import datetime, timezone, timedelta

class AuthService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Fetch a user from the database by email address."""
        return db.query(User).filter(User.email == email).first()

    @classmethod
    def register_user(cls, db: Session, user_data: UserCreate) -> User:
        """Register a new user after verifying email uniqueness and password strength."""
        existing_user = cls.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )
        
        # Validate password strength
        try:
            validate_password_strength(user_data.password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Hash user password
        hashed_pwd = get_password_hash(user_data.password)
        
        # Create and save user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_pwd
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @classmethod
    def authenticate_user(cls, db: Session, login_data: UserLogin) -> User:
        """Authenticate user email and password."""
        cls.cleanup_expired_tokens(db)
        user = cls.get_user_by_email(db, login_data.email)
        if not user or not user.password_hash or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @classmethod
    def request_password_reset(cls, db: Session, email: str) -> str:
        """Generate a cryptographically secure reset token for the email if user exists."""
        cls.cleanup_expired_tokens(db)
        user = cls.get_user_by_email(db, email)
        if not user:
            return ""
            
        # Clean up any existing tokens for this user
        db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()
            
        token = secrets.token_urlsafe(64)
        hashed_token = hashlib.sha256(token.encode('utf-8')).hexdigest()
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=hashed_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db.add(reset_token)
        db.commit()
        return token

    @classmethod
    def confirm_password_reset(cls, db: Session, email: str, token: str, new_password: str) -> None:
        """Verify the token and update user's password."""
        user = cls.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
            
        hashed_token = hashlib.sha256(token.encode('utf-8')).hexdigest()
            
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.token == hashed_token
        ).first()
            
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token."
            )
            
        if reset_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            db.delete(reset_token)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token."
            )
            
        # Validate password strength
        try:
            validate_password_strength(new_password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
            
        # Update user's password
        user.password_hash = get_password_hash(new_password)
        
        # Clear the token after use
        db.delete(reset_token)
        db.commit()

    @classmethod
    def cleanup_expired_tokens(cls, db: Session) -> int:
        """Remove all expired reset tokens from the database."""
        result = db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.now(timezone.utc)
        ).delete()
        db.commit()
        return result

    @classmethod
    def authenticate_or_create_oauth_user(cls, db: Session, oauth_data: OAuthLoginRequest) -> User:
        """Find or create a user based on OAuth data."""
        # Find user by email first
        user = cls.get_user_by_email(db, oauth_data.email)
        if user:
            # If user exists, ensure they are linked to this OAuth provider
            if not user.oauth_provider:
                user.oauth_provider = oauth_data.provider
                user.oauth_id = oauth_data.oauth_id
                db.commit()
                db.refresh(user)
            elif user.oauth_provider != oauth_data.provider:
                # User exists but is signed up with another provider
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"This email is already registered using {user.oauth_provider}."
                )
            return user
            
        # Create a new user if they do not exist
        new_user = User(
            name=oauth_data.name,
            email=oauth_data.email,
            oauth_provider=oauth_data.provider,
            oauth_id=oauth_data.oauth_id,
            password_hash=None
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
