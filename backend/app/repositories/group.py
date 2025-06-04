from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.schemas import Group, GroupCreate, GroupUpdate
import asyncpg

class GroupRepository(BaseRepository[Group]):
    @property
    def table_name(self) -> str:
        return "Groups"

    @property
    def model_class(self):
        return Group

    async def create_group(
        self,
        group: GroupCreate,
        conn: Optional[asyncpg.Connection] = None
    ) -> Group:
        query = """
            INSERT INTO Groups (
                SubdivisionID, Name, Year
            ) VALUES ($1, $2, $3)
            RETURNING *
        """
        values = (
            group.SubdivisionID,
            group.Name,
            group.Year
        )
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            return Group(**dict(row))

    async def update_group(
        self,
        id: int,
        group: GroupUpdate,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[Group]:
        update_fields = []
        values = []
        param_count = 1

        for field, value in group.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_count}")
            values.append(value)
            param_count += 1

        if not update_fields:
            return await self.get_by_id(id)

        values.append(id)
        query = f"""
            UPDATE Groups 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING *
        """

        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            return Group(**dict(row)) if row else None

    async def get_groups_by_subdivision(
        self,
        subdivision_id: int,
        limit: int = 100,
        offset: int = 0,
        conn: Optional[asyncpg.Connection] = None
    ) -> List[Group]:
        query = """
            SELECT g.*, s.Name as SubdivisionName
            FROM Groups g
            JOIN Subdivisions s ON g.SubdivisionID = s.ID
            WHERE g.SubdivisionID = $1
            ORDER BY g.Name
            LIMIT $2 OFFSET $3
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, subdivision_id, limit, offset)
            return [Group(**dict(row)) for row in rows]

    async def get_group_with_details(
        self,
        id: int,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[Group]:
        query = """
            SELECT 
                g.*,
                s.Name as SubdivisionName,
                COUNT(st.ID) as StudentsCount,
                COUNT(CASE WHEN st.IsActive THEN 1 END) as ActiveStudentsCount
            FROM Groups g
            JOIN Subdivisions s ON g.SubdivisionID = s.ID
            LEFT JOIN Students st ON g.ID = st.GroupID
            WHERE g.ID = $1
            GROUP BY g.ID, s.ID
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return Group(**dict(row)) if row else None

    async def get_group(self, group_id: int) -> Optional[dict]:
        query = "SELECT * FROM groups WHERE id = $1"
        record = await self.fetchrow(query, group_id)
        return dict(record) if record else None

    async def get_groups_by_division(self, division_id: int) -> List[dict]:
        query = """
        SELECT g.*, 
               COUNT(s.id) as student_count,
               COUNT(CASE WHEN s.is_union_member THEN 1 END) as union_members_count
        FROM groups g
        LEFT JOIN students s ON s.group_id = g.id
        WHERE g.division_id = $1
        GROUP BY g.id
        ORDER BY g.name
        """
        records = await self.fetch(query, division_id)
        return [dict(record) for record in records]

    async def delete_group(self, group_id: int) -> bool:
        query = "DELETE FROM groups WHERE id = $1"
        result = await self.execute(query, group_id)
        return "DELETE 1" in result

    async def get_group_statistics(self, group_id: int) -> dict:
        query = """
        SELECT 
            g.id,
            g.name,
            g.year_of_study,
            COUNT(s.id) as total_students,
            COUNT(CASE WHEN s.is_union_member THEN 1 END) as union_members
        FROM groups g
        LEFT JOIN students s ON s.group_id = g.id
        WHERE g.id = $1
        GROUP BY g.id, g.name, g.year_of_study
        """
        record = await self.fetchrow(query, group_id)
        return dict(record) if record else None 