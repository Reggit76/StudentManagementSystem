#!/usr/bin/env python3
"""
Скрипт инициализации системы - создание базы данных и начальных данных
"""
import asyncio
import asyncpg
from loguru import logger
import sys
import os

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import get_password_hash


async def init_database():
    """Инициализация базы данных"""
    try:
        # Подключаемся к PostgreSQL
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT
        )
        
        logger.info("Connected to database successfully")
        
        # Проверяем, есть ли таблицы
        tables_exist = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
        """)
        
        if not tables_exist:
            logger.warning("Tables don't exist. Please run migrations first.")
            return False
        
        # Роли уже созданы миграциями, но проверяем их наличие
        default_roles = [
            'CHAIRMAN',
            'DEPUTY_CHAIRMAN', 
            'DIVISION_HEAD',
            'DORMITORY_HEAD'
        ]
        
        for role_name in default_roles:
            existing_role = await conn.fetchrow(
                "SELECT id FROM roles WHERE name = $1", role_name
            )
            if existing_role:
                logger.info(f"Role exists: {role_name} (ID: {existing_role['id']})")
            else:
                logger.warning(f"Role missing: {role_name}")
        
        # Создаем администратора (председателя профкома)
        admin_exists = await conn.fetchrow(
            "SELECT id FROM users WHERE login = $1", 
            settings.FIRST_SUPERUSER_USERNAME
        )
        
        if not admin_exists:
            password_hash = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
            
            # Создаем пользователя
            user_id = await conn.fetchval("""
                INSERT INTO users (login, passwordhash) 
                VALUES ($1, $2) 
                RETURNING id
            """, settings.FIRST_SUPERUSER_USERNAME, password_hash)
            
            # Назначаем роль председателя профкома
            chairman_role = await conn.fetchrow(
                "SELECT id FROM roles WHERE name = 'CHAIRMAN'"
            )
            
            if chairman_role:
                await conn.execute("""
                    INSERT INTO userroles (userid, roleid) 
                    VALUES ($1, $2)
                """, user_id, chairman_role['id'])
                logger.info(f"Assigned CHAIRMAN role to user {user_id}")
            
            logger.info(f"Created admin user: {settings.FIRST_SUPERUSER_USERNAME}")
        else:
            logger.info("Admin user already exists")
        
        # Создаем тестовое подразделение
        test_subdivision = await conn.fetchrow(
            "SELECT id FROM subdivisions WHERE name = $1", 
            "Тестовое подразделение"
        )
        
        if not test_subdivision:
            subdivision_id = await conn.fetchval("""
                INSERT INTO subdivisions (name) 
                VALUES ($1) 
                RETURNING id
            """, "Тестовое подразделение")
            logger.info(f"Created test subdivision (ID: {subdivision_id})")
        
        # Дополнительные статусы уже созданы миграциями
        await conn.close()
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(init_database())
    if not success:
        sys.exit(1)