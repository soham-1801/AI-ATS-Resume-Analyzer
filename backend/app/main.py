import os
import time
import logging
from collections import defaultdict
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.init_db import init_db
from app.api import auth, resume, ats, dashboard, ai, job_description
from app.database.connection import get_db

logger = logging.getLogger("ats.api")

# Initialize database tables automatically on startup
init_db()


app = FastAPI(
    title="AI Resume ATS API",
    description="Backend API for parsing resumes and calculating ATS alignment scores.",
    version="1.0.0"
)

# CORS Middleware Configuration
allowed_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# If wildcard is set or for generic allow
env = os.getenv("ENVIRONMENT", "development")
if "*" in allowed_origins:
    if env == "production":
        raise ValueError("Wildcard CORS ('*') is strictly forbidden in production.")
    else:
        allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    max_age=3600,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust Middleware-based Rate Limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Simple Request Logging
    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    
    return response

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(ats.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(job_description.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Resume ATS API!",
        "docs_url": "/docs",
        "status": "healthy"
    }

@app.get("/health")
def health_check(response: Response, db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception:
        response.status_code = 503
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }

