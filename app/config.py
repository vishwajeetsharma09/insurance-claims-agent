"""
Configuration settings for the insurance claims processing agent.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Configuration
    api_title: str = "Insurance Claims Processing Agent"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Gemini Configuration
    gemini_api_key: str
    gemini_model_name: str = "gemini-2.5-flash"
    gemini_extraction_temperature: float = 0.0
    gemini_reasoning_temperature: float = 0.2
    gemini_max_retries: int = 3
    
    # Business Rules Configuration
    fast_track_threshold: float = 25000.0
    investigation_keywords: List[str] = ["fraud", "inconsistent", "staged"]
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# Global settings instance
settings = Settings()

