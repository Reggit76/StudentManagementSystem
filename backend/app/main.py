from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys
import os

from .core.config import settings
from .core.database import db
from .core.exceptions import AppException
from .core.migrations import migration_manager
from .api.v1 import api_router
from .middleware.security import SecurityHeadersMiddleware


# Настройка логирования
logger.remove()
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

if settings.LOG_FILE:
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

# Создание приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API для управления данными профсоюза студентов",
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Добавляем middleware для безопасности
app.add_middleware(SecurityHeadersMiddleware)


# Обработчики исключений
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Обработчик пользовательских исключений"""
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "code": exc.code
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений"""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Общий обработчик исключений"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )


# События жизненного цикла
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("Starting Student Union Management System...")
    
    try:
        await db.connect()
        logger.info("Database connection established")
        
        # Запускаем миграции если включен AUTO_MIGRATE
        if os.getenv("AUTO_MIGRATE", "false").lower() == "true":
            logger.info("Running database migrations...")
            await migration_manager.run_migrations()
            logger.info("Database migrations completed")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    logger.info("Shutting down Student Union Management System...")
    
    try:
        await db.disconnect()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")


# Подключение роутеров
app.include_router(api_router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Student Union Management System API",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    try:
        # Проверяем подключение к БД
        async with db.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.APP_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/migrations/status")
async def migrations_status():
    """Проверка статуса миграций"""
    try:
        await migration_manager.ensure_migrations_table()
        applied = await migration_manager.get_applied_migrations()
        pending = await migration_manager.get_pending_migrations()
        
        return {
            "applied_migrations": applied,
            "pending_migrations": [p.name for p in pending],
            "total_applied": len(applied),
            "total_pending": len(pending)
        }
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get migration status"}
        )