"""Configuration management for the Todo AI application."""
import os
import logging
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    model: str = os.getenv("MODEL", "claude-3-haiku-20240307")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
    
    # App Configuration
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS settings
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)