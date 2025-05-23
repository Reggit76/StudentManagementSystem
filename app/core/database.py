import asyncpg
from asyncpg import Pool
from typing import Optional
from contextlib import asynccontextmanager
from loguru import logger
from ..config import settings


class Database:
    """Класс для работы с БД"""
    
    def __init__(self):
        self.pool: Optional[Pool] = None
    
    async def connect(self):
        """Создать пул соединений с БД"""
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                min_size=10,
                max_size=20,
                command_timeout=60
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
        async with self.pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager
    async def transaction(self):
        """Создать транзакцию"""
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                yield connection
    
    async def execute(self, query: str, *args):
        """Выполнить запрос"""
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Получить несколько записей"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Получить одну запись"""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Получить одно значение"""
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)
        

# Глобальный экземпляр базы данных
db = Database()