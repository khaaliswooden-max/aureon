"""Application configuration using Pydantic settings."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Aureon API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Database
    database_url: str = "postgresql://aureon:aureon_dev_password@localhost:5432/aureon"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 3600
    
    # SAM.gov API
    sam_gov_api_key: Optional[str] = None
    sam_gov_base_url: str = "https://api.sam.gov/opportunities/v2"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-opus-20240229"
    
    # Scoring Configuration
    relevance_score_weights: dict = {
        "naics": 0.25,
        "semantic": 0.30,
        "geographic": 0.15,
        "size": 0.15,
        "past_performance": 0.15
    }
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

