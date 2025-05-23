from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # База данных
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "student_union"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DATABASE_URL: Optional[str] = None
    
    # Приложение
    APP_NAME: str = "Student Union System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CSRF
    CSRF_SECRET_KEY: str = "your-csrf-secret-key-here"
    CSRF_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def async_database_url(self) -> str:
        """Получить URL для asyncpg"""
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (с кешированием)"""
    return Settings()


settings = get_settings()