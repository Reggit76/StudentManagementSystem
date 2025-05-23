from typing import Optional, List, Dict, Any, TypeVar, Generic, Type
from asyncpg import Connection, Pool
from abc import ABC, abstractmethod
import asyncpg
from loguru import logger

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Базовый репозиторий с общими CRUD операциями"""
    
    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Имя таблицы в БД"""
        pass
    
    @property
    @abstractmethod
    def model_class(self) -> Type[T]:
        """Класс модели Pydantic"""
        pass
    
    async def get_by_id(self, id: int, conn: Optional[Connection] = None) -> Optional[T]:
        """Получить запись по ID"""
        query = f"SELECT * FROM {self.table_name} WHERE id = $1"
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return self.model_class(**dict(row)) if row else None
    
    async def get_all(
        self, 
        limit: int = 100, 
        offset: int = 0,
        order_by: str = "id",
        order_desc: bool = False,
        conn: Optional[Connection] = None
    ) -> List[T]:
        """Получить все записи с пагинацией"""
        order = "DESC" if order_desc else "ASC"
        query = f"""
            SELECT * FROM {self.table_name} 
            ORDER BY {order_by} {order}
            LIMIT $1 OFFSET $2
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, limit, offset)
            return [self.model_class(**dict(row)) for row in rows]
    
    async def count(self, filters: Optional[Dict[str, Any]] = None, conn: Optional[Connection] = None) -> int:
        """Подсчитать количество записей"""
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        params = []
        
        if filters:
            where_clause, params = self._build_where_clause(filters)
            query += f" WHERE {where_clause}"
        
        async with self._get_connection(conn) as connection:
            result = await connection.fetchval(query, *params)
            return result
    
    async def exists(self, id: int, conn: Optional[Connection] = None) -> bool:
        """Проверить существование записи"""
        query = f"SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE id = $1)"
        
        async with self._get_connection(conn) as connection:
            return await connection.fetchval(query, id)
    
    async def delete(self, id: int, conn: Optional[Connection] = None) -> bool:
        """Удалить запись по ID"""
        query = f"DELETE FROM {self.table_name} WHERE id = $1 RETURNING id"
        
        async with self._get_connection(conn) as connection:
            result = await connection.fetchval(query, id)
            return result is not None
    
    async def delete_many(self, ids: List[int], conn: Optional[Connection] = None) -> int:
        """Удалить несколько записей"""
        query = f"DELETE FROM {self.table_name} WHERE id = ANY($1)"
        
        async with self._get_connection(conn) as connection:
            result = await connection.execute(query, ids)
            return int(result.split()[-1])  # Извлекаем количество удаленных строк
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> tuple[str, list]:
        """Построить WHERE clause из фильтров"""
        conditions = []
        params = []
        param_count = 1
        
        for field, value in filters.items():
            if value is None:
                conditions.append(f"{field} IS NULL")
            elif isinstance(value, list):
                conditions.append(f"{field} = ANY(${param_count})")
                params.append(value)
                param_count += 1
            else:
                conditions.append(f"{field} = ${param_count}")
                params.append(value)
                param_count += 1
        
        where_clause = " AND ".join(conditions)
        return where_clause, params
    
    async def _get_connection(self, conn: Optional[Connection]) -> Connection:
        """Получить соединение с БД"""
        if conn:
            return conn
        return self.db_pool
    
    async def execute_query(self, query: str, *args, conn: Optional[Connection] = None):
        """Выполнить произвольный запрос"""
        async with self._get_connection(conn) as connection:
            return await connection.fetch(query, *args)
    
    async def execute_many(self, query: str, args_list: List[tuple], conn: Optional[Connection] = None):
        """Выполнить запрос для множества параметров"""
        async with self._get_connection(conn) as connection:
            return await connection.executemany(query, args_list)