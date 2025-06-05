from typing import Optional, List, Dict, Any
from asyncpg import Connection
from .base import BaseRepository
from ..models.hostel_student import HostelStudent, HostelStudentCreate, HostelStudentUpdate


class HostelRepository(BaseRepository[HostelStudent]):
    """Репозиторий для работы с проживающими в общежитии"""
    
    @property
    def table_name(self) -> str:
        return "hostelstudents"
    
    @property
    def model_class(self):
        return HostelStudent
    
    async def create(self, data: HostelStudentCreate, conn: Optional[Connection] = None) -> HostelStudent:
        """Создать запись о проживании в общежитии"""
        query = """
            INSERT INTO hostelstudents (studentid, hostel, room, comment) 
            VALUES ($1, $2, $3, $4) 
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(
                query,
                data.studentid,
                data.hostel,
                data.room,
                data.comment
            )
            return await self.get_with_student_name(row['id'], connection)
    
    async def update(self, id: int, data: HostelStudentUpdate, conn: Optional[Connection] = None) -> Optional[HostelStudent]:
        """Обновить запись о проживании в общежитии"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_with_student_name(id, conn)
        
        set_parts = []
        values = [id]
        for i, (field, value) in enumerate(update_data.items()):
            set_parts.append(f"{field} = ${i+2}")
            values.append(value)
        
        query = f"""
            UPDATE hostelstudents 
            SET {', '.join(set_parts)}
            WHERE id = $1
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            return await self.get_with_student_name(row['id'], connection) if row else None
    
    async def get_by_student_id(self, student_id: int, conn: Optional[Connection] = None) -> Optional[HostelStudent]:
        """Получить запись о проживании по ID студента"""
        query = """
            SELECT h.*, s.fullname as student_name
            FROM hostelstudents h
            JOIN students s ON s.id = h.studentid
            WHERE h.studentid = $1
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, student_id)
            return HostelStudent(**dict(row)) if row else None
    
    async def get_with_student_name(self, id: int, conn: Optional[Connection] = None) -> Optional[HostelStudent]:
        """Получить запись с именем студента"""
        query = """
            SELECT h.*, s.fullname as student_name
            FROM hostelstudents h
            JOIN students s ON s.id = h.studentid
            WHERE h.id = $1
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return HostelStudent(**dict(row)) if row else None
    
    async def get_by_hostel(self, hostel: int, conn: Optional[Connection] = None) -> List[HostelStudent]:
        """Получить всех проживающих в общежитии"""
        query = """
            SELECT h.*, s.fullname as student_name
            FROM hostelstudents h
            JOIN students s ON s.id = h.studentid
            WHERE h.hostel = $1
            ORDER BY h.room, s.fullname
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, hostel)
            return [HostelStudent(**dict(row)) for row in rows]
    
    async def get_by_room(self, hostel: int, room: int, conn: Optional[Connection] = None) -> List[HostelStudent]:
        """Получить всех проживающих в комнате"""
        query = """
            SELECT h.*, s.fullname as student_name
            FROM hostelstudents h
            JOIN students s ON s.id = h.studentid
            WHERE h.hostel = $1 AND h.room = $2
            ORDER BY s.fullname
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, hostel, room)
            return [HostelStudent(**dict(row)) for row in rows]
    
    async def search(self, filters: Dict[str, Any], conn: Optional[Connection] = None) -> List[HostelStudent]:
        """Поиск проживающих по фильтрам"""
        query = """
            SELECT h.*, s.fullname as student_name
            FROM hostelstudents h
            JOIN students s ON s.id = h.studentid
            WHERE 1=1
        """
        
        params = []
        param_count = 1
        
        if 'hostel' in filters:
            query += f" AND h.hostel = ${param_count}"
            params.append(filters['hostel'])
            param_count += 1
        
        if 'room' in filters:
            query += f" AND h.room = ${param_count}"
            params.append(filters['room'])
            param_count += 1
        
        if 'student_name' in filters:
            query += f" AND s.fullname ILIKE ${param_count}"
            params.append(f"%{filters['student_name']}%")
            param_count += 1
        
        query += " ORDER BY h.hostel, h.room, s.fullname"
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [HostelStudent(**dict(row)) for row in rows]