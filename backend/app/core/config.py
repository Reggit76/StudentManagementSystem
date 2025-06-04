from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Приложение
    PROJECT_NAME: str = "Student Union Management System"
    API_V1_STR: str = "/api/v1"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # База данных
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "student_union"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    
    # Пул соединений
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20
    DB_POOL_MAX_QUERIES: int = 50000
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_COMMAND_TIMEOUT: int = 60
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CSRF
    CSRF_SECRET_KEY: str = "your-csrf-secret-key-here-change-in-production"
    CSRF_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Первый пользователь-администратор
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    FIRST_SUPERUSER_USERNAME: str = "admin"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (с кешированием)"""
    return Settings()


settings = get_settings()