from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.schemas import Student, StudentCreate, StudentUpdate
import asyncpg

class StudentRepository(BaseRepository[Student]):
    @property
    def table_name(self) -> str:
        return "Students"

    @property
    def model_class(self):
        return Student

    async def create_student(
        self,
        student: StudentCreate,
        conn: Optional[asyncpg.Connection] = None
    ) -> Student:
        query = """
            INSERT INTO Students (
                GroupID, FullName, IsActive, IsBudget, Year
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING *
        """
        values = (
            student.GroupID,
            student.FullName,
            student.IsActive,
            student.IsBudget,
            student.Year
        )
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            
            if student.Data:
                data_query = """
                    INSERT INTO StudentData (
                        Phone, Email, Birthday
                    ) VALUES ($1, $2, $3)
                    RETURNING ID
                """
                data_values = (
                    student.Data.Phone,
                    student.Data.Email,
                    student.Data.Birthday
                )
                data_id = await connection.fetchval(data_query, *data_values)
                
                # Обновляем DataID в Students
                await connection.execute(
                    "UPDATE Students SET DataID = $1 WHERE ID = $2",
                    data_id, row['id']
                )
                
            return Student(**dict(row))

    async def update_student(
        self,
        id: int,
        student: StudentUpdate,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[Student]:
        update_fields = []
        values = []
        param_count = 1

        for field, value in student.dict(exclude_unset=True).items():
            if field != "Data":
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1

        if not update_fields:
            return await self.get_by_id(id)

        values.append(id)
        query = f"""
            UPDATE Students 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING *
        """

        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            
            if student.Data and row:
                data_update_fields = []
                data_values = []
                data_param_count = 1
                
                for field, value in student.Data.dict(exclude_unset=True).items():
                    data_update_fields.append(f"{field} = ${data_param_count}")
                    data_values.append(value)
                    data_param_count += 1
                
                if data_update_fields:
                    data_values.append(row['DataID'])
                    data_query = f"""
                        UPDATE StudentData 
                        SET {', '.join(data_update_fields)}
                        WHERE id = ${data_param_count}
                    """
                    await connection.execute(data_query, *data_values)
            
            return Student(**dict(row)) if row else None

    async def get_student_with_details(
        self,
        id: int,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[Student]:
        query = """
            SELECT 
                s.*,
                sd.Phone, sd.Email, sd.Birthday,
                hs.Hostel, hs.Room, hs.Comment,
                g.Name as GroupName,
                array_agg(DISTINCT ast.Name) as AdditionalStatuses
            FROM Students s
            LEFT JOIN StudentData sd ON s.DataID = sd.ID
            LEFT JOIN HostelStudents hs ON s.ID = hs.StudentID
            LEFT JOIN Groups g ON s.GroupID = g.ID
            LEFT JOIN StudentAdditionalStatuses sas ON s.ID = sas.StudentID
            LEFT JOIN AdditionalStatuses ast ON sas.StatusID = ast.ID
            WHERE s.ID = $1
            GROUP BY s.ID, sd.ID, hs.ID, g.ID
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return Student(**dict(row)) if row else None

    async def get_students_by_group(
        self,
        group_id: int,
        limit: int = 100,
        offset: int = 0,
        conn: Optional[asyncpg.Connection] = None
    ) -> List[Student]:
        query = """
            SELECT * FROM Students
            WHERE GroupID = $1
            ORDER BY FullName
            LIMIT $2 OFFSET $3
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, group_id, limit, offset)
            return [Student(**dict(row)) for row in rows]

    async def get_students_by_subdivision(
        self,
        subdivision_id: int,
        limit: int = 100,
        offset: int = 0,
        conn: Optional[asyncpg.Connection] = None
    ) -> List[Student]:
        query = """
            SELECT s.* FROM Students s
            JOIN Groups g ON s.GroupID = g.ID
            WHERE g.SubdivisionID = $1
            ORDER BY s.FullName
            LIMIT $2 OFFSET $3
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, subdivision_id, limit, offset)
            return [Student(**dict(row)) for row in rows]

    async def get_student(self, student_id: int) -> Optional[dict]:
        query = "SELECT * FROM students WHERE id = $1"
        record = await self.fetchrow(query, student_id)
        return dict(record) if record else None

    async def get_students_by_division(self, division_id: int) -> List[dict]:
        query = """
        SELECT s.* FROM students s
        JOIN groups g ON s.group_id = g.id
        WHERE g.division_id = $1
        ORDER BY g.name, s.last_name, s.first_name
        """
        records = await self.fetch(query, division_id)
        return [dict(record) for record in records]

    async def delete_student(self, student_id: int) -> bool:
        query = "DELETE FROM students WHERE id = $1"
        result = await self.execute(query, student_id)
        return "DELETE 1" in result

    async def get_union_members_count_by_division(self, division_id: int) -> int:
        query = """
        SELECT COUNT(*) FROM students s
        JOIN groups g ON s.group_id = g.id
        WHERE g.division_id = $1 AND s.is_union_member = true
        """
        return await self.fetchval(query, division_id)

    async def get_students_count_by_division(self, division_id: int) -> int:
        query = """
        SELECT COUNT(*) FROM students s
        JOIN groups g ON s.group_id = g.id
        WHERE g.division_id = $1
        """
        return await self.fetchval(query, division_id) 