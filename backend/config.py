import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Settings:
    """Application settings"""
    # Database
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:password@localhost:5432/healthcare_dev'
    )

    # JWT
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_HOURS: int = 24

    # App
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    APP_NAME: str = 'Healthcare API'
    APP_VERSION: str = '1.0.0'

    # Gemini API (for educational chat assistant)
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')

settings = Settings()
