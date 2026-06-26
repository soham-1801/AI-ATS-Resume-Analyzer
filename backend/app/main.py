import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.init_db import init_db
from app.api import auth, resume, ats, dashboard, ai, job_description

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
if "*" in allowed_origins:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    max_age=3600,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

