# backend/app/core/migrations.py

import os
import asyncio
from pathlib import Path
from typing import List
from loguru import logger
from .database import db
from .config import settings


class MigrationManager:
    """Менеджер миграций"""
    
    def __init__(self, migrations_dir: str = None):
        if migrations_dir is None:
            # Определяем путь к migrations относительно местоположения файла
            current_dir = Path(__file__).parent.parent.parent  # Поднимаемся к корню backend
            migrations_dir = current_dir / "migrations"
        
        self.migrations_dir = Path(migrations_dir)
        logger.info(f"Using migrations directory: {self.migrations_dir}")
        
    async def ensure_migrations_table(self):
        """Создать таблицу для отслеживания миграций"""
        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await db.execute(query)
        
    async def get_applied_migrations(self) -> List[str]:
        """Получить список уже примененных миграций"""
        try:
            rows = await db.fetch(
                "SELECT filename FROM schema_migrations ORDER BY filename"
            )
            return [row['filename'] for row in rows]
        except Exception:
            # Если таблица не существует, возвращаем пустой список
            return []
    
    async def get_pending_migrations(self) -> List[Path]:
        """Получить список миграций для применения"""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory {self.migrations_dir} does not exist")
            return []
        
        applied = await self.get_applied_migrations()
        all_migrations = sorted([
            f for f in self.migrations_dir.glob("*.sql")
            if f.is_file()
        ])
        
        pending = [
            migration for migration in all_migrations
            if migration.name not in applied
        ]
        
        return pending
    
    async def apply_migration(self, migration_file: Path):
        """Применить одну миграцию"""
        logger.info(f"Applying migration: {migration_file.name}")
        
        try:
            # Читаем содержимое файла миграции
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Разделяем на отдельные команды (по точке с запятой)
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            # Выполняем в транзакции
            async with db.transaction() as conn:
                for command in commands:
                    if command:
                        await conn.execute(command)
                
                # Записываем в таблицу миграций
                await conn.execute(
                    "INSERT INTO schema_migrations (filename) VALUES ($1)",
                    migration_file.name
                )
            
            logger.info(f"Successfully applied migration: {migration_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_file.name}: {e}")
            raise
    
    async def run_migrations(self):
        """Запустить все ожидающие миграции"""
        try:
            await self.ensure_migrations_table()
            pending = await self.get_pending_migrations()
            
            if not pending:
                logger.info("No pending migrations")
                return
            
            logger.info(f"Found {len(pending)} pending migrations")
            
            for migration in pending:
                await self.apply_migration(migration)
            
            logger.info("All migrations applied successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


# Глобальный экземпляр менеджера миграций
migration_manager = MigrationManager()