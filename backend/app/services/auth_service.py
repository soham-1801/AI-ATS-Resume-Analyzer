from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.schemas.auth_schema import UserLogin, OAuthLoginRequest
from app.utils.security import get_password_hash, verify_password, validate_password_strength
import secrets

# In-memory store for password reset tokens: maps email.lower() -> token (6-char string)
RESET_TOKENS = {}

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
        user = cls.get_user_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @classmethod
    def request_password_reset(cls, db: Session, email: str) -> str:
        """Generate a random 6-character reset token for the email if user exists."""
        user = cls.get_user_by_email(db, email)
        if not user:
            return ""
            
        token = secrets.token_hex(3).upper() # 6 characters
        RESET_TOKENS[email.lower()] = token
        print(f"\n[PASSWORD RESET] Generated reset token for {email}: {token}\n")
        return token

    @classmethod
    def confirm_password_reset(cls, db: Session, email: str, token: str, new_password: str) -> None:
        """Verify the token and update user's password."""
        email_lower = email.lower()
        saved_token = RESET_TOKENS.get(email_lower)
        
        if not saved_token or saved_token != token.upper():
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
            
        user = cls.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
            
        # Update user's password
        user.password_hash = get_password_hash(new_password)
        db.commit()
        
        # Clear the token after use
        RESET_TOKENS.pop(email_lower, None)

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
            password_hash=get_password_hash(secrets.token_hex(16))  # Satisfy NOT NULL constraint securely
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
