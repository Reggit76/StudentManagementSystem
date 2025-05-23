from typing import Optional, List
from asyncpg import Connection
from .base import BaseRepository
from ..models.additional_status import AdditionalStatus, AdditionalStatusCreate, AdditionalStatusUpdate


class AdditionalStatusRepository(BaseRepository[AdditionalStatus]):
    """Репозиторий для работы с дополнительными статусами"""
    
    @property
    def table_name(self) -> str:
        return "additionalstatuses"
    
    @property
    def model_class(self):
        return AdditionalStatus
    
    async def create(self, data: AdditionalStatusCreate, conn: Optional[Connection] = None) -> AdditionalStatus:
        """Создать дополнительный статус"""
        query = """
            INSERT INTO additionalstatuses (name) 
            VALUES ($1) 
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, data.name)
            return AdditionalStatus(**dict(row))
    
    async def update(self, id: int, data: AdditionalStatusUpdate, conn: Optional[Connection] = None) -> Optional[AdditionalStatus]:
        """Обновить дополнительный статус"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(id, conn)
        
        query = """
            UPDATE additionalstatuses 
            SET name = $2
            WHERE id = $1
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id, data.name)
            return AdditionalStatus(**dict(row)) if row else None
    
    async def get_by_name(self, name: str, conn: Optional[Connection] = None) -> Optional[AdditionalStatus]:
        """Получить статус по имени"""
        query = "SELECT * FROM additionalstatuses WHERE name = $1"
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, name)
            return AdditionalStatus(**dict(row)) if row else None
    
    async def get_by_student_id(self, student_id: int, conn: Optional[Connection] = None) -> List[AdditionalStatus]:
        """Получить статусы студента"""
        query = """
            SELECT a.* FROM additionalstatuses a
            JOIN studentadditionalstatuses sas ON sas.statusid = a.id
            WHERE sas.studentid = $1
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, student_id)
            return [AdditionalStatus(**dict(row)) for row in rows]