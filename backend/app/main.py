import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.init_db import init_db
from app.api import auth, resume, ats, dashboard, ai, job_description
from app.database.connection import get_db
from app.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ats.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AI Resume ATS API...")
    settings.validate_production()
    logger.info("Environment configurations validated.")
    
    init_db()
    logger.info("Database initialized.")
    yield
    # Shutdown
    logger.info("Shutting down AI Resume ATS API...")

app = FastAPI(
    title="AI Resume ATS API",
    description="Backend API for parsing resumes and calculating ATS alignment scores.",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware Configuration
allowed_origins = [origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

if "*" in allowed_origins:
    if settings.ENVIRONMENT == "production":
        raise ValueError("Wildcard CORS ('*') is strictly forbidden in production.")
    else:
        allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust Middleware-based Rate Limiting
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

from fastapi import HTTPException
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    logger.error(f"Unhandled exception during request {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
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
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        response.status_code = 503
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }
