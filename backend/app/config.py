"""
Configuration management for the Todo AI application.

This module uses Pydantic's BaseSettings to manage application configuration.
It loads settings from environment variables and a .env file, allowing for flexible
deployment and development environments. It also configures the application-wide logger.
"""
import os
import logging
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    Provides default values for a seamless development experience.
    """
    
    # --- LLM Provider Configuration ---
    # The API key for the Anthropic Claude API.
    # Optional: The application has a fallback mechanism if the key is not provided.
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # The specific model to be used for the LLM-powered features.
    # Defaults to a cost-effective and fast model.
    model: str = os.getenv("MODEL", "claude-3-haiku-20240307")
    
    # --- Database Configuration ---
    # The connection string for the database.
    # Defaults to a local SQLite database file inside the /data volume.
    database_url: str = os.getenv("DATABASE_URL", "sqlite:////data/tasks.db")
    
    # --- Application Behavior ---
    # Enable or disable debug mode.
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    # The logging level for the application.
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # --- Security / CORS ---
    # A list of allowed origins for Cross-Origin Resource Sharing (CORS).
    # This is crucial for allowing the frontend to communicate with the backend.
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        """Pydantic model configuration."""
        env_file = ".env"
        case_sensitive = False

# A single, globally accessible instance of the application settings.
settings = Settings()

# --- Logger Setup ---
# Configure the root logger for the application based on the settings.
# This ensures consistent logging format and level across all modules.
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# A specific logger for the config module, can be used for logging config-related events.
logger = logging.getLogger(__name__)