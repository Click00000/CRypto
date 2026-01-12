from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 168  # 7 days
    
    # App URLs
    APP_BASE_URL: str
    API_BASE_URL: str
    
    # Email
    RESEND_API_KEY: str
    EMAIL_FROM: str
    
    # EVM
    EVM_RPC_URL: str
    
    # Bitcoin
    BTC_MODE: str = "CORE_RPC"  # CORE_RPC or EXPLORER
    BTC_RPC_URL: str = ""
    BTC_RPC_USER: str = ""
    BTC_RPC_PASS: str = ""
    BTC_EXPLORER_BASE_URL: str = ""
    BTC_EXPLORER_API_KEY: str = ""
    
    # Admin
    ADMIN_EMAIL: str
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow reading from environment even if .env doesn't exist (for production)
        extra = "ignore"


settings = Settings()
