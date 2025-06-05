#!/usr/bin/env python3
"""
Скрипт для ручного запуска миграций
"""
import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к приложению
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app.core.database import db
from app.core.migrations import migration_manager
from loguru import logger


async def run_migrations():
    """Запуск миграций"""
    try:
        logger.info("Connecting to database...")
        await db.connect()
        
        logger.info("Running migrations...")
        await migration_manager.run_migrations()
        
        logger.info("Migrations completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        await db.disconnect()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(run_migrations())
    if not success:
        sys.exit(1)