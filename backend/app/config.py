import os
import logging

class Settings:
    def __init__(self):
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dummy_secret_key_for_testing")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
        
        # Hardcoded configs
        self.VERSION = "1.0.0"
        self.RATE_LIMIT = "100/minute"

    def validate_production(self):
        """Validates that critical env vars are set and secure for production."""
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "dummy_secret_key_for_testing":
                raise ValueError("CRITICAL: Default SECRET_KEY is not allowed in production!")
            
            if not self.DATABASE_URL:
                raise ValueError("CRITICAL: DATABASE_URL is missing in production!")

            if not self.GEMINI_API_KEY:
                logging.warning("GEMINI_API_KEY is missing. AI features may fail.")

settings = Settings()
