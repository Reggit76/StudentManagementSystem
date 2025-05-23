from typing import Optional, List, Dict, Any
from asyncpg import Connection
from .base import BaseRepository
from ..models.subdivision import Subdivision, SubdivisionCreate, SubdivisionUpdate, SubdivisionWithStats


class SubdivisionRepository(BaseRepository[Subdivision]):
    """Репозиторий для работы с подразделениями"""
    
    @property
    def table_name(self) -> str:
        return "subdivisions"
    
    @property
    def model_class(self):
        return Subdivision
    
    async def create(self, data: SubdivisionCreate, conn: Optional[Connection] = None) -> Subdivision:
        """Создать подразделение"""
        query = """
            INSERT INTO subdivisions (name) 
            VALUES ($1) 
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, data.name)
            return Subdivision(**dict(row))
    
    async def update(self, id: int, data: SubdivisionUpdate, conn: Optional[Connection] = None) -> Optional[Subdivision]:
        """Обновить подразделение"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(id, conn)
        
        set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(update_data.keys())])
        query = f"""
            UPDATE subdivisions 
            SET {set_clause}
            WHERE id = $1
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id, *update_data.values())
            return Subdivision(**dict(row)) if row else None
    
    async def get_by_name(self, name: str, conn: Optional[Connection] = None) -> Optional[Subdivision]:
        """Получить подразделение по имени"""
        query = "SELECT * FROM subdivisions WHERE name = $1"
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, name)
            return Subdivision(**dict(row)) if row else None
    
    async def get_with_stats(self, id: int, conn: Optional[Connection] = None) -> Optional[SubdivisionWithStats]:
        """Получить подразделение со статистикой"""
        query = """
            SELECT 
                s.*,
                COUNT(DISTINCT g.id) as groups_count,
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT u.id) as users_count
            FROM subdivisions s
            LEFT JOIN groups g ON g.subdivisionid = s.id
            LEFT JOIN students st ON st.groupid = g.id
            LEFT JOIN users u ON u.subdivisionid = s.id
            WHERE s.id = $1
            GROUP BY s.id
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return SubdivisionWithStats(**dict(row)) if row else None
    
    async def get_all_with_stats(self, conn: Optional[Connection] = None) -> List[SubdivisionWithStats]:
        """Получить все подразделения со статистикой"""
        query = """
            SELECT 
                s.*,
                COUNT(DISTINCT g.id) as groups_count,
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT u.id) as users_count
            FROM subdivisions s
            LEFT JOIN groups g ON g.subdivisionid = s.id
            LEFT JOIN students st ON st.groupid = g.id
            LEFT JOIN users u ON u.subdivisionid = s.id
            GROUP BY s.id
            ORDER BY s.name
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query)
            return [SubdivisionWithStats(**dict(row)) for row in rows]
