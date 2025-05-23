from typing import Optional, List, Dict, Any
from asyncpg import Connection
from .base import BaseRepository
from ..models.group import Group, GroupCreate, GroupUpdate, GroupWithStats


class GroupRepository(BaseRepository[Group]):
    """Репозиторий для работы с группами"""
    
    @property
    def table_name(self) -> str:
        return "groups"
    
    @property
    def model_class(self):
        return Group
    
    async def create(self, data: GroupCreate, conn: Optional[Connection] = None) -> Group:
        """Создать группу"""
        query = """
            INSERT INTO groups (subdivisionid, name, year) 
            VALUES ($1, $2, $3) 
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(
                query, 
                data.subdivision_id, 
                data.name, 
                data.year
            )
            return Group(**dict(row))
    
    async def update(self, id: int, data: GroupUpdate, conn: Optional[Connection] = None) -> Optional[Group]:
        """Обновить группу"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(id, conn)
        
        # Маппинг имен полей
        field_mapping = {
            'subdivision_id': 'subdivisionid'
        }
        
        set_parts = []
        values = [id]
        for i, (field, value) in enumerate(update_data.items()):
            db_field = field_mapping.get(field, field)
            set_parts.append(f"{db_field} = ${i+2}")
            values.append(value)
        
        query = f"""
            UPDATE groups 
            SET {', '.join(set_parts)}
            WHERE id = $1
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            return Group(**dict(row)) if row else None
    
    async def get_by_name(self, name: str, conn: Optional[Connection] = None) -> Optional[Group]:
        """Получить группу по имени"""
        query = "SELECT * FROM groups WHERE name = $1"
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, name)
            return Group(**dict(row)) if row else None
    
    async def get_by_subdivision(self, subdivision_id: int, year: Optional[int] = None, conn: Optional[Connection] = None) -> List[Group]:
        """Получить группы подразделения"""
        if year:
            query = "SELECT * FROM groups WHERE subdivisionid = $1 AND year = $2 ORDER BY name"
            params = [subdivision_id, year]
        else:
            query = "SELECT * FROM groups WHERE subdivisionid = $1 ORDER BY name"
            params = [subdivision_id]
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [Group(**dict(row)) for row in rows]
    
    async def get_with_stats(self, id: int, conn: Optional[Connection] = None) -> Optional[GroupWithStats]:
        """Получить группу со статистикой"""
        query = """
            SELECT 
                g.*,
                s.name as subdivision_name,
                COUNT(st.id) as students_count,
                COUNT(st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                COUNT(st.id) FILTER (WHERE st.isbudget = true) as budget_students_count
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
            WHERE g.id = $1
            GROUP BY g.id, s.name
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return GroupWithStats(**dict(row)) if row else None
    
    async def get_all_with_stats(self, year: Optional[int] = None, conn: Optional[Connection] = None) -> List[GroupWithStats]:
        """Получить все группы со статистикой"""
        base_query = """
            SELECT 
                g.*,
                s.name as subdivision_name,
                COUNT(st.id) as students_count,
                COUNT(st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                COUNT(st.id) FILTER (WHERE st.isbudget = true) as budget_students_count
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
        """
        
        if year:
            query = base_query + " WHERE g.year = $1 GROUP BY g.id, s.name ORDER BY g.name"
            params = [year]
        else:
            query = base_query + " GROUP BY g.id, s.name ORDER BY g.name"
            params = []
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [GroupWithStats(**dict(row)) for row in rows]
