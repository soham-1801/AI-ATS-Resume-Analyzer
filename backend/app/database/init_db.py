import sys
import os

# Adjust Python path if script is run directly to ensure local imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.exc import SQLAlchemyError
from app.database.database import Base, engine
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.ats_result import ATSResult
from app.models.password_reset_token import PasswordResetToken


def init_db():
    """Create all tables defined in the models on the database."""
    print("Connecting to the database and creating tables...")
    try:
        env = os.getenv("ENVIRONMENT", "development")
        if env != "production":
            Base.metadata.create_all(bind=engine)
            print("All database tables created successfully (development mode)!")
        else:
            print("Production mode detected. Please use Alembic migrations instead of create_all().")
    except SQLAlchemyError as e:
        print(f"Error occurred during database initialization: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    init_db()
