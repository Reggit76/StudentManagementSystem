from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.schemas import Subdivision, SubdivisionCreate, SubdivisionUpdate
import asyncpg

class DivisionRepository(BaseRepository[Subdivision]):
    @property
    def table_name(self) -> str:
        return "Subdivisions"

    @property
    def model_class(self):
        return Subdivision

    async def create_division(
        self,
        division: SubdivisionCreate,
        conn: Optional[asyncpg.Connection] = None
    ) -> Subdivision:
        query = """
            INSERT INTO Subdivisions (
                Name, Type
            ) VALUES ($1, $2)
            RETURNING *
        """
        values = (
            division.Name,
            division.Type
        )
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            return Subdivision(**dict(row))

    async def update_division(
        self,
        id: int,
        division: SubdivisionUpdate,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[Subdivision]:
        update_fields = []
        values = []
        param_count = 1

        for field, value in division.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_count}")
            values.append(value)
            param_count += 1

        if not update_fields:
            return await self.get_by_id(id)

        values.append(id)
        query = f"""
            UPDATE Subdivisions 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING *
        """

        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            return Subdivision(**dict(row)) if row else None

    async def get_division_with_stats(
        self,
        id: int,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[Subdivision]:
        query = """
            SELECT 
                s.*,
                COUNT(DISTINCT g.ID) as GroupsCount,
                COUNT(DISTINCT st.ID) as StudentsCount,
                COUNT(DISTINCT CASE WHEN st.IsActive THEN st.ID END) as ActiveStudentsCount
            FROM Subdivisions s
            LEFT JOIN Groups g ON s.ID = g.SubdivisionID
            LEFT JOIN Students st ON g.ID = st.GroupID
            WHERE s.ID = $1
            GROUP BY s.ID
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return Subdivision(**dict(row)) if row else None

    async def get_divisions_by_type(
        self,
        type: str,
        limit: int = 100,
        offset: int = 0,
        conn: Optional[asyncpg.Connection] = None
    ) -> List[Subdivision]:
        query = """
            SELECT * FROM Subdivisions
            WHERE Type = $1
            ORDER BY Name
            LIMIT $2 OFFSET $3
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, type, limit, offset)
            return [Subdivision(**dict(row)) for row in rows]

    async def get_division_users(
        self,
        id: int,
        limit: int = 100,
        offset: int = 0,
        conn: Optional[asyncpg.Connection] = None
    ) -> List[dict]:
        query = """
            SELECT 
                u.*,
                array_agg(r.Name) as Roles
            FROM Users u
            LEFT JOIN UserRoles ur ON u.ID = ur.UserID
            LEFT JOIN Roles r ON ur.RoleID = r.ID
            WHERE u.SubdivisionID = $1
            GROUP BY u.ID
            ORDER BY u.Login
            LIMIT $2 OFFSET $3
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, id, limit, offset)
            return [dict(row) for row in rows] 