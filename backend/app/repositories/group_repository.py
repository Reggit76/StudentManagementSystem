# backend/app/repositories/group_repository.py

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
                data.subdivisionid, 
                data.name, 
                data.year
            )
            
            # Получаем группу с дополнительной информацией
            return await self._get_group_with_subdivision(row['id'], connection)
    
    async def update(self, id: int, data: GroupUpdate, conn: Optional[Connection] = None) -> Optional[Group]:
        """Обновить группу"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(id, conn)
        
        # Маппинг полей для корректного обновления
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
            if not row:
                return None
            return await self._get_group_with_subdivision(row['id'], connection)
    
    async def get_by_id(self, id: int, conn: Optional[Connection] = None) -> Optional[Group]:
        """Получить группу по ID с дополнительной информацией"""
        async with self._get_connection(conn) as connection:
            return await self._get_group_with_subdivision(id, connection)
    
    async def get_by_name(self, name: str, conn: Optional[Connection] = None) -> Optional[Group]:
        """Получить группу по имени"""
        query = """
            SELECT 
                g.*,
                s.name as subdivision_name,
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                CASE 
                    WHEN COUNT(DISTINCT st.id) > 0 
                    THEN ROUND((COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) * 100.0) / COUNT(DISTINCT st.id), 1)
                    ELSE 0 
                END as union_percentage
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
            WHERE g.name = $1
            GROUP BY g.id, s.id, s.name
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, name)
            return Group(**dict(row)) if row else None
    
    async def get_by_subdivision(
        self, 
        subdivision_id: int, 
        year: Optional[int] = None, 
        limit: int = 100,
        offset: int = 0,
        conn: Optional[Connection] = None
    ) -> List[Group]:
        """Получить группы подразделения"""
        base_query = """
            SELECT 
                g.*,
                s.name as subdivision_name,
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                CASE 
                    WHEN COUNT(DISTINCT st.id) > 0 
                    THEN ROUND((COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) * 100.0) / COUNT(DISTINCT st.id), 1)
                    ELSE 0 
                END as union_percentage
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
            WHERE g.subdivisionid = $1
        """
        
        params = [subdivision_id]
        param_count = 2
        
        if year:
            base_query += f" AND g.year = ${param_count}"
            params.append(year)
            param_count += 1
        
        query = base_query + f"""
            GROUP BY g.id, s.id, s.name
            ORDER BY g.name
            LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([limit, offset])
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [Group(**dict(row)) for row in rows]
    
    async def get_with_stats(self, id: int, conn: Optional[Connection] = None) -> Optional[GroupWithStats]:
        """Получить группу со статистикой"""
        query = """
            SELECT 
                g.*,
                s.name as subdivision_name,
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isbudget = true) as budget_students_count,
                CASE 
                    WHEN COUNT(DISTINCT st.id) > 0 
                    THEN ROUND((COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) * 100.0) / COUNT(DISTINCT st.id), 1)
                    ELSE 0 
                END as union_percentage
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
            WHERE g.id = $1
            GROUP BY g.id, s.id, s.name
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
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isbudget = true) as budget_students_count,
                CASE 
                    WHEN COUNT(DISTINCT st.id) > 0 
                    THEN ROUND((COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) * 100.0) / COUNT(DISTINCT st.id), 1)
                    ELSE 0 
                END as union_percentage
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
        """
        
        if year:
            query = base_query + " WHERE g.year = $1 GROUP BY g.id, s.id, s.name ORDER BY g.name"
            params = [year]
        else:
            query = base_query + " GROUP BY g.id, s.id, s.name ORDER BY g.name"
            params = []
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [GroupWithStats(**dict(row)) for row in rows]
    
    async def get_all(
        self, 
        limit: int = 100, 
        offset: int = 0,
        order_by: str = "name",
        order_desc: bool = False,
        conn: Optional[Connection] = None
    ) -> List[Group]:
        """Получить все записи с пагинацией и статистикой"""
        order = "DESC" if order_desc else "ASC"
        query = f"""
            SELECT 
                g.*,
                s.name as subdivision_name,
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                CASE 
                    WHEN COUNT(DISTINCT st.id) > 0 
                    THEN ROUND((COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) * 100.0) / COUNT(DISTINCT st.id), 1)
                    ELSE 0 
                END as union_percentage
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
            GROUP BY g.id, s.id, s.name
            ORDER BY g.{order_by} {order}
            LIMIT $1 OFFSET $2
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, limit, offset)
            return [Group(**dict(row)) for row in rows]
    
    async def _get_group_with_subdivision(self, id: int, conn: Connection) -> Optional[Group]:
        """Внутренний метод для получения группы с информацией о подразделении"""
        query = """
            SELECT 
                g.*,
                s.name as subdivision_name,
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                CASE 
                    WHEN COUNT(DISTINCT st.id) > 0 
                    THEN ROUND((COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) * 100.0) / COUNT(DISTINCT st.id), 1)
                    ELSE 0 
                END as union_percentage
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
            WHERE g.id = $1
            GROUP BY g.id, s.id, s.name
        """
        
        row = await conn.fetchrow(query, id)
        return Group(**dict(row)) if row else None

    async def count(self, filters: Optional[Dict[str, Any]] = None, conn: Optional[Connection] = None) -> int:
        """Подсчитать количество групп с учетом фильтров"""
        query = "SELECT COUNT(*) FROM groups WHERE 1=1"
        
        params = []
        param_count = 1
        
        if filters:
            if 'subdivision_id' in filters:
                query += f" AND subdivisionid = ${param_count}"
                params.append(filters['subdivision_id'])
                param_count += 1
            
            if 'year' in filters:
                query += f" AND year = ${param_count}"
                params.append(filters['year'])
                param_count += 1
        
        async with self._get_connection(conn) as connection:
            return await connection.fetchval(query, *params)

    async def search(
        self, 
        filters: Dict[str, Any], 
        limit: int = 100, 
        offset: int = 0,
        conn: Optional[Connection] = None
    ) -> List[Group]:
        """Поиск групп по фильтрам"""
        query = """
            SELECT 
                g.*,
                s.name as subdivision_name,
                COUNT(DISTINCT st.id) as students_count,
                COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) as active_students_count,
                CASE 
                    WHEN COUNT(DISTINCT st.id) > 0 
                    THEN ROUND((COUNT(DISTINCT st.id) FILTER (WHERE st.isactive = true) * 100.0) / COUNT(DISTINCT st.id), 1)
                    ELSE 0 
                END as union_percentage
            FROM groups g
            LEFT JOIN subdivisions s ON s.id = g.subdivisionid
            LEFT JOIN students st ON st.groupid = g.id
            WHERE 1=1
        """
        
        params = []
        param_count = 1
        
        # Добавляем фильтры
        if 'subdivision_id' in filters:
            query += f" AND g.subdivisionid = ${param_count}"
            params.append(filters['subdivision_id'])
            param_count += 1
        
        if 'year' in filters:
            query += f" AND g.year = ${param_count}"
            params.append(filters['year'])
            param_count += 1
        
        if 'search' in filters:
            query += f" AND g.name ILIKE ${param_count}"
            params.append(f"%{filters['search']}%")
            param_count += 1
        
        # Добавляем группировку, сортировку и пагинацию
        query += f"""
            GROUP BY g.id, s.id, s.name
            ORDER BY g.name 
            LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([limit, offset])
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [Group(**dict(row)) for row in rows]