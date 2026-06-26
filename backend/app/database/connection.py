from app.database.database import SessionLocal

def get_db():
    """
    FastAPI dependency that provides a transactional database session.
    It yields a database session and automatically closes it after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
