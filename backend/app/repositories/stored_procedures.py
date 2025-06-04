# backend/app/repositories/stored_procedures.py

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date
from asyncpg import Connection
from .student_repository import StudentRepository
from .contribution_repository import ContributionRepository


class StoredProceduresMixin:
    """Миксин для работы с хранимыми процедурами"""
    
    async def call_procedure(
        self, 
        proc_name: str, 
        *args, 
        conn: Optional[Connection] = None
    ) -> Any:
        """Вызвать хранимую процедуру"""
        query = f"CALL {proc_name}({', '.join(['$' + str(i+1) for i in range(len(args))])})"
        
        async with self._get_connection(conn) as connection:
            return await connection.fetch(query, *args)
    
    async def call_function(
        self, 
        func_name: str, 
        *args, 
        conn: Optional[Connection] = None
    ) -> Any:
        """Вызвать хранимую функцию"""
        placeholders = ', '.join(['$' + str(i+1) for i in range(len(args))])
        query = f"SELECT * FROM {func_name}({placeholders})"
        
        async with self._get_connection(conn) as connection:
            return await connection.fetch(query, *args)


# Пример расширенного репозитория студентов с хранимыми процедурами
class StudentRepositoryWithProcedures(StudentRepository, StoredProceduresMixin):
    """Репозиторий студентов с поддержкой хранимых процедур"""
    
    async def transfer_student_to_group(
        self, 
        student_id: int, 
        new_group_id: int,
        user_id: int,
        conn: Optional[Connection] = None
    ) -> bool:
        """
        Перевести студента в другую группу через хранимую процедуру.
        Процедура проверяет права доступа и логирует изменения.
        """
        query = "SELECT transfer_student_to_group($1, $2, $3)"
        
        async with self._get_connection(conn) as connection:
            result = await connection.fetchval(query, student_id, new_group_id, user_id)
            return result
    
    async def bulk_activate_students(
        self,
        student_ids: List[int],
        user_id: int,
        conn: Optional[Connection] = None
    ) -> Dict[str, Any]:
        """
        Массовая активация студентов через хранимую процедуру.
        Возвращает количество успешно активированных и ошибки.
        """
        query = "SELECT * FROM bulk_activate_students($1::integer[], $2)"
        
        async with self._get_connection(conn) as connection:
            result = await connection.fetchrow(query, student_ids, user_id)
            return dict(result)
    
    async def get_students_with_debt(
        self,
        subdivision_id: Optional[int] = None,
        year: int = 2024,
        conn: Optional[Connection] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить студентов с задолженностью через хранимую функцию.
        Функция выполняет сложные вычисления на стороне БД.
        """
        if subdivision_id:
            query = "SELECT * FROM get_students_with_debt($1, $2)"
            params = [subdivision_id, year]
        else:
            query = "SELECT * FROM get_students_with_debt(NULL, $1)"
            params = [year]
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [dict(row) for row in rows]


# Пример расширенного репозитория взносов с хранимыми процедурами  
class ContributionRepositoryWithProcedures(ContributionRepository, StoredProceduresMixin):
    """Репозиторий взносов с поддержкой хранимых процедур"""
    
    async def process_bulk_payment(
        self,
        group_id: int,
        semester: int,
        amount: Decimal,
        payment_date: date,
        user_id: int,
        conn: Optional[Connection] = None
    ) -> Dict[str, Any]:
        """
        Обработать массовый платеж для группы через хранимую процедуру.
        Процедура создает взносы для всех активных студентов группы.
        """
        query = "SELECT * FROM process_bulk_payment($1, $2, $3, $4, $5)"
        
        async with self._get_connection(conn) as connection:
            result = await connection.fetchrow(
                query, 
                group_id, 
                semester, 
                amount, 
                payment_date, 
                user_id
            )
            return dict(result)
    
    async def generate_payment_report(
        self,
        subdivision_id: int,
        year: int,
        semester: int,
        conn: Optional[Connection] = None
    ) -> List[Dict[str, Any]]:
        """
        Сгенерировать отчет по платежам через хранимую функцию.
        Функция выполняет агрегацию и форматирование на стороне БД.
        """
        query = "SELECT * FROM generate_payment_report($1, $2, $3)"
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, subdivision_id, year, semester)
            return [dict(row) for row in rows]
    
    async def calculate_debt_summary(
        self,
        as_of_date: Optional[date] = None,
        conn: Optional[Connection] = None
    ) -> Dict[str, Any]:
        """
        Рассчитать общую сводку по задолженностям.
        Использует хранимую функцию для сложных вычислений.
        """
        if not as_of_date:
            as_of_date = date.today()
        
        query = "SELECT * FROM calculate_debt_summary($1)"
        
        async with self._get_connection(conn) as connection:
            result = await connection.fetchrow(query, as_of_date)
            return dict(result)


# Пример работы с системными хранимыми процедурами
class SystemProcedures:
    """Класс для работы с системными хранимыми процедурами"""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def check_user_permission(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        action: str
    ) -> bool:
        """
        Проверить права пользователя через хранимую функцию.
        Централизованная проверка прав на уровне БД.
        """
        query = "SELECT check_user_permission($1, $2, $3, $4)"
        
        async with self.db_pool.acquire() as conn:
            return await conn.fetchval(query, user_id, resource_type, resource_id, action)
    
    async def log_user_action(
        self,
        user_id: int,
        action: str,
        table_name: str,
        record_id: int,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Записать действие пользователя в журнал через процедуру.
        """
        import json
        
        query = "CALL log_user_action($1, $2, $3, $4, $5, $6)"
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                user_id,
                action,
                table_name,
                record_id,
                json.dumps(old_data) if old_data else None,
                json.dumps(new_data) if new_data else None
            )
    
    async def cleanup_expired_tokens(self) -> int:
        """
        Очистить истекшие токены через хранимую процедуру.
        Возвращает количество удаленных токенов.
        """
        query = "SELECT cleanup_expired_tokens()"
        
        async with self.db_pool.acquire() as conn:
            return await conn.fetchval(query)
    
    async def rotate_user_sessions(self, days_to_keep: int = 30) -> Dict[str, int]:
        """
        Ротация пользовательских сессий.
        Архивирует старые сессии и удаляет очень старые.
        """
        query = "SELECT * FROM rotate_user_sessions($1)"
        
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow(query, days_to_keep)
            return dict(result)