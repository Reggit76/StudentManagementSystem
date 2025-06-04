import asyncpg
from asyncpg import Pool
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from loguru import logger
from app.core.config import settings
from fastapi import Depends

class Database:
    """Класс для работы с БД"""
    
    def __init__(self):
        self.pool: Optional[Pool] = None
    
    async def connect(self):
        """Создать пул соединений с БД"""
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.POSTGRES_SERVER,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=settings.DB_POOL_COMMAND_TIMEOUT
            )
            logger.info("Database pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    async def disconnect(self):
        """Закрыть пул соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """Получить соединение из пула"""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager
    async def transaction(self):
        """Создать транзакцию"""
        async with self.acquire() as connection:
            async with connection.transaction():
                yield connection
    
    async def execute(self, query: str, *args):
        """Выполнить запрос"""
        async with self.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Получить несколько записей"""
        async with self.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Получить одну запись"""
        async with self.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Получить одно значение"""
        async with self.acquire() as connection:
            return await connection.fetchval(query, *args)

# Создаем глобальный экземпляр базы данных
db = Database()

async def get_db():
    """Dependency для получения соединения с БД"""
    async with db.acquire() as conn:
        yield conn