"""
Configuration module for KrishiLok Backend
Loads environment variables and provides app configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "krishilok_db"
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Upload Configuration
    UPLOAD_FOLDER: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB in bytes
    
    # CORS Configuration
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # OpenRouter API Configuration (for AI-powered treatment advice)
    OPENROUTER_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
