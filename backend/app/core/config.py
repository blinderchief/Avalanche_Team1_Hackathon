"""
Core configuration management for SpectraQ Agent Backend
"""

from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment (development/production)")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    RELOAD: bool = Field(default=False, description="Auto-reload in development")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://username:password@localhost:5432/spectraq_agent",
        description="Database connection URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API key"
    )
    GEMINI_BASE_URL: str = Field(
        default="https://generativelanguage.googleapis.com",
        description="Gemini API base URL"
    )
    
    # MCP Configuration
    MCP_SERVERS_CONFIG_PATH: str = Field(
        default="./config/mcp_servers.json",
        description="Path to MCP servers configuration file"
    )
    
    # External API Keys
    CRYPTOPANIC_API_KEY: str = Field(default="", description="CryptoPanic API key")
    CRYPTOPANIC_API_PLAN: str = Field(default="free", description="CryptoPanic API plan")
    FIRECRAWL_API_KEY: str = Field(default="", description="Firecrawl API key")
    
    # Security
    SECRET_KEY: str = Field(
        default="your_super_secret_key_here_change_in_production",
        description="Secret key for JWT tokens"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Logging format")
    
    # Celery Configuration
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL"
    )
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,https://spectraq.io",
        description="Comma-separated list of allowed CORS origins"
    )
    
    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit per minute per client"
    )
    
    # Model Configuration
    DEFAULT_MODEL: str = Field(default="gemini-2.0-flash-exp", description="Default LLM model")
    MAX_TOKENS: int = Field(default=4096, description="Maximum tokens per request")
    TEMPERATURE: float = Field(default=0.7, description="LLM temperature")
    
    # Session Management
    SESSION_TIMEOUT_MINUTES: int = Field(
        default=60,
        description="Session timeout in minutes"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
