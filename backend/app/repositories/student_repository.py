# backend/app/repositories/student_repository.py

from typing import Optional, List, Dict, Any
from asyncpg import Connection
from .base import BaseRepository
from ..models.student import Student, StudentCreate, StudentUpdate, StudentWithDetails
from ..models.student_data import StudentData
from ..models.additional_status import AdditionalStatus
from ..models.hostel_student import HostelStudent
from ..models.contribution import Contribution


class StudentRepository(BaseRepository[Student]):
    """Репозиторий для работы со студентами"""
    
    @property
    def table_name(self) -> str:
        return "students"
    
    @property
    def model_class(self):
        return Student
    
    async def create(self, data: StudentCreate, conn: Optional[Connection] = None) -> Student:
        """Создать студента"""
        async with self._get_connection(conn) as connection:
            async with connection.transaction():
                # Создаем данные студента, если переданы
                data_id = None
                if data.student_data:
                    data_query = """
                        INSERT INTO studentdata (phone, email, birthday) 
                        VALUES ($1, $2, $3) 
                        RETURNING id
                    """
                    data_id = await connection.fetchval(
                        data_query,
                        data.student_data.phone,
                        data.student_data.email,
                        data.student_data.birthday
                    )
                
                # Создаем студента
                student_query = """
                    INSERT INTO students (groupid, fullname, isactive, isbudget, dataid, year) 
                    VALUES ($1, $2, $3, $4, $5, $6) 
                    RETURNING *
                """
                student_row = await connection.fetchrow(
                    student_query,
                    data.groupid,
                    data.fullname,
                    data.isactive,
                    data.isbudget,
                    data_id,
                    data.year
                )
                
                # Добавляем дополнительные статусы
                if data.additional_status_ids:
                    status_query = """
                        INSERT INTO studentadditionalstatuses (studentid, statusid) 
                        VALUES ($1, $2)
                    """
                    status_data = [(student_row['id'], status_id) for status_id in data.additional_status_ids]
                    await connection.executemany(status_query, status_data)
                
                # Добавляем информацию об общежитии, если есть
                if hasattr(data, 'hostel_data') and data.hostel_data:
                    hostel_query = """
                        INSERT INTO hostelstudents (studentid, hostel, room, comment) 
                        VALUES ($1, $2, $3, $4)
                    """
                    await connection.execute(
                        hostel_query,
                        student_row['id'],
                        data.hostel_data.get('hostel'),
                        data.hostel_data.get('room'),
                        data.hostel_data.get('comment', '')
                    )
                
                # Возвращаем полные данные студента
                return await self.get_with_details(student_row['id'], connection)
    
    async def create_with_hostel(self, data: dict, conn: Optional[Connection] = None) -> Student:
        """Создать студента с информацией об общежитии (для API)"""
        async with self._get_connection(conn) as connection:
            async with connection.transaction():
                # Создаем данные студента, если переданы
                data_id = None
                if data.get('student_data'):
                    student_data = data['student_data']
                    data_query = """
                        INSERT INTO studentdata (phone, email, birthday) 
                        VALUES ($1, $2, $3) 
                        RETURNING id
                    """
                    data_id = await connection.fetchval(
                        data_query,
                        student_data.get('phone'),
                        student_data.get('email'),
                        student_data.get('birthday')
                    )
                
                # Создаем студента
                student_query = """
                    INSERT INTO students (groupid, fullname, isactive, isbudget, dataid, year) 
                    VALUES ($1, $2, $3, $4, $5, $6) 
                    RETURNING *
                """
                student_row = await connection.fetchrow(
                    student_query,
                    data.get('group_id'),
                    data.get('full_name'),
                    data.get('is_active', False),
                    data.get('is_budget', True),
                    data_id,
                    data.get('year', 2024)
                )
                
                # Добавляем дополнительные статусы
                if data.get('additional_status_ids'):
                    status_query = """
                        INSERT INTO studentadditionalstatuses (studentid, statusid) 
                        VALUES ($1, $2)
                    """
                    status_data = [(student_row['id'], status_id) for status_id in data['additional_status_ids']]
                    await connection.executemany(status_query, status_data)
                
                # Добавляем информацию об общежитии, если есть
                if data.get('hostel_data'):
                    hostel_data = data['hostel_data']
                    hostel_query = """
                        INSERT INTO hostelstudents (studentid, hostel, room, comment) 
                        VALUES ($1, $2, $3, $4)
                    """
                    await connection.execute(
                        hostel_query,
                        student_row['id'],
                        hostel_data.get('hostel'),
                        hostel_data.get('room'),
                        hostel_data.get('comment', '')
                    )
                
                # Возвращаем полные данные студента
                return await self.get_with_details(student_row['id'], connection)
    
    async def update(self, id: int, data: StudentUpdate, conn: Optional[Connection] = None) -> Optional[Student]:
        """Обновить студента"""
        async with self._get_connection(conn) as connection:
            async with connection.transaction():
                # Получаем текущие данные студента
                current = await self.get_by_id(id, connection)
                if not current:
                    return None
                
                # Обновляем данные студента, если переданы
                if data.student_data:
                    if current.dataid:
                        # Обновляем существующие данные
                        data_update = data.student_data.model_dump(exclude_unset=True)
                        if data_update:
                            set_parts = []
                            values = [current.dataid]
                            for i, (field, value) in enumerate(data_update.items()):
                                set_parts.append(f"{field} = ${i+2}")
                                values.append(value)
                            
                            data_query = f"""
                                UPDATE studentdata 
                                SET {', '.join(set_parts)}
                                WHERE id = $1
                            """
                            await connection.execute(data_query, *values)
                    else:
                        # Создаем новые данные
                        data_query = """
                            INSERT INTO studentdata (phone, email, birthday) 
                            VALUES ($1, $2, $3) 
                            RETURNING id
                        """
                        data_id = await connection.fetchval(
                            data_query,
                            data.student_data.phone,
                            data.student_data.email,
                            data.student_data.birthday
                        )
                        # Обновляем ссылку в students
                        await connection.execute(
                            "UPDATE students SET dataid = $1 WHERE id = $2",
                            data_id, id
                        )
                
                # Обновляем основные данные студента
                update_data = data.model_dump(exclude_unset=True, exclude={'student_data', 'additional_status_ids'})
                if update_data:
                    set_parts = []
                    values = [id]
                    for i, (field, value) in enumerate(update_data.items()):
                        set_parts.append(f"{field} = ${i+2}")
                        values.append(value)
                    
                    query = f"""
                        UPDATE students 
                        SET {', '.join(set_parts)}
                        WHERE id = $1
                    """
                    await connection.execute(query, *values)
                
                # Обновляем дополнительные статусы
                if data.additional_status_ids is not None:
                    # Удаляем старые статусы
                    await connection.execute(
                        "DELETE FROM studentadditionalstatuses WHERE studentid = $1", 
                        id
                    )
                    
                    # Добавляем новые статусы
                    if data.additional_status_ids:
                        status_query = """
                            INSERT INTO studentadditionalstatuses (studentid, statusid) 
                            VALUES ($1, $2)
                        """
                        status_data = [(id, status_id) for status_id in data.additional_status_ids]
                        await connection.executemany(status_query, status_data)
                
                return await self.get_with_details(id, connection)
    
    async def update_with_hostel(self, id: int, data: dict, conn: Optional[Connection] = None) -> Optional[Student]:
        """Обновить студента с информацией об общежитии (для API)"""
        async with self._get_connection(conn) as connection:
            async with connection.transaction():
                # Получаем текущие данные студента
                current = await self.get_by_id(id, connection)
                if not current:
                    return None
                
                # Обновляем данные студента, если переданы
                if data.get('student_data'):
                    student_data = data['student_data']
                    if current.dataid:
                        # Обновляем существующие данные
                        data_update = {k: v for k, v in student_data.items() if v is not None}
                        if data_update:
                            set_parts = []
                            values = [current.dataid]
                            for i, (field, value) in enumerate(data_update.items()):
                                set_parts.append(f"{field} = ${i+2}")
                                values.append(value)
                            
                            data_query = f"""
                                UPDATE studentdata 
                                SET {', '.join(set_parts)}
                                WHERE id = $1
                            """
                            await connection.execute(data_query, *values)
                    else:
                        # Создаем новые данные
                        data_query = """
                            INSERT INTO studentdata (phone, email, birthday) 
                            VALUES ($1, $2, $3) 
                            RETURNING id
                        """
                        data_id = await connection.fetchval(
                            data_query,
                            student_data.get('phone'),
                            student_data.get('email'),
                            student_data.get('birthday')
                        )
                        # Обновляем ссылку в students
                        await connection.execute(
                            "UPDATE students SET dataid = $1 WHERE id = $2",
                            data_id, id
                        )
                
                # Обновляем основные данные студента
                main_fields = ['group_id', 'full_name', 'is_active', 'is_budget', 'year']
                update_data = {k: v for k, v in data.items() if k in main_fields and v is not None}
                
                # Маппинг полей
                field_mapping = {
                    'group_id': 'groupid',
                    'full_name': 'fullname',
                    'is_active': 'isactive',
                    'is_budget': 'isbudget'
                }
                
                if update_data:
                    set_parts = []
                    values = [id]
                    for i, (field, value) in enumerate(update_data.items()):
                        db_field = field_mapping.get(field, field)
                        set_parts.append(f"{db_field} = ${i+2}")
                        values.append(value)
                    
                    query = f"""
                        UPDATE students 
                        SET {', '.join(set_parts)}
                        WHERE id = $1
                    """
                    await connection.execute(query, *values)
                
                # Обновляем дополнительные статусы
                if 'additional_status_ids' in data:
                    # Удаляем старые статусы
                    await connection.execute(
                        "DELETE FROM studentadditionalstatuses WHERE studentid = $1", 
                        id
                    )
                    
                    # Добавляем новые статусы
                    if data['additional_status_ids']:
                        status_query = """
                            INSERT INTO studentadditionalstatuses (studentid, statusid) 
                            VALUES ($1, $2)
                        """
                        status_data = [(id, status_id) for status_id in data['additional_status_ids']]
                        await connection.executemany(status_query, status_data)
                
                # Обновляем информацию об общежитии
                if 'hostel_data' in data:
                    # Удаляем старую запись об общежитии
                    await connection.execute(
                        "DELETE FROM hostelstudents WHERE studentid = $1",
                        id
                    )
                    
                    # Добавляем новую запись, если есть данные
                    if data['hostel_data'] and data['hostel_data'].get('hostel'):
                        hostel_data = data['hostel_data']
                        hostel_query = """
                            INSERT INTO hostelstudents (studentid, hostel, room, comment) 
                            VALUES ($1, $2, $3, $4)
                        """
                        await connection.execute(
                            hostel_query,
                            id,
                            hostel_data.get('hostel'),
                            hostel_data.get('room'),
                            hostel_data.get('comment', '')
                        )
                
                return await self.get_with_details(id, connection)
    
    async def get_with_details(self, id: int, conn: Optional[Connection] = None) -> Optional[Student]:
        """Получить студента с полными данными"""
        query = """
            SELECT 
                s.*,
                g.name as group_name,
                sub.name as subdivision_name,
                sd.phone, sd.email, sd.birthday
            FROM students s
            JOIN groups g ON g.id = s.groupid
            JOIN subdivisions sub ON sub.id = g.subdivisionid
            LEFT JOIN studentdata sd ON sd.id = s.dataid
            WHERE s.id = $1
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            if not row:
                return None
            
            # Формируем данные студента
            student_data = dict(row)
            
            # Добавляем студенческие данные
            if student_data['dataid']:
                student_data['student_data'] = StudentData(
                    id=student_data['dataid'],
                    phone=student_data.pop('phone'),
                    email=student_data.pop('email'),
                    birthday=student_data.pop('birthday'),
                    created_at=student_data['created_at'],
                    updated_at=student_data['updated_at']
                )
            else:
                student_data.pop('phone', None)
                student_data.pop('email', None)
                student_data.pop('birthday', None)
                student_data['student_data'] = None
            
            # Получаем дополнительные статусы
            statuses = await self._get_student_statuses(id, connection)
            student_data['additional_statuses'] = statuses
            
            return Student(**student_data)
    
    async def get_with_full_details(self, id: int, conn: Optional[Connection] = None) -> Optional[StudentWithDetails]:
        """Получить студента с полными деталями включая общежитие и взносы"""
        student = await self.get_with_details(id, conn)
        if not student:
            return None
        
        async with self._get_connection(conn) as connection:
            # Получаем информацию об общежитии
            hostel_query = "SELECT * FROM hostelstudents WHERE studentid = $1"
            hostel_row = await connection.fetchrow(hostel_query, id)
            
            # Получаем взносы
            contributions_query = """
                SELECT * FROM contributions 
                WHERE studentid = $1 
                ORDER BY year DESC, semester DESC
            """
            contribution_rows = await connection.fetch(contributions_query, id)
            
            return StudentWithDetails(
                **student.model_dump(),
                hostel_info=HostelStudent(**dict(hostel_row)) if hostel_row else None,
                contributions=[Contribution(**dict(row)) for row in contribution_rows]
            )
    
    async def search(
        self, 
        filters: Dict[str, Any], 
        limit: int = 100, 
        offset: int = 0,
        conn: Optional[Connection] = None
    ) -> List[Student]:
        """Поиск студентов по фильтрам"""
        query = """
            SELECT 
                s.*,
                g.name as group_name,
                sub.name as subdivision_name,
                sd.phone, sd.email, sd.birthday
            FROM students s
            JOIN groups g ON g.id = s.groupid
            JOIN subdivisions sub ON sub.id = g.subdivisionid
            LEFT JOIN studentdata sd ON sd.id = s.dataid
            WHERE 1=1
        """
        
        params = []
        param_count = 1
        
        # Добавляем фильтры
        if 'group_id' in filters:
            query += f" AND s.groupid = ${param_count}"
            params.append(filters['group_id'])
            param_count += 1
        
        if 'subdivision_id' in filters:
            query += f" AND g.subdivisionid = ${param_count}"
            params.append(filters['subdivision_id'])
            param_count += 1
        
        if 'is_active' in filters:
            query += f" AND s.isactive = ${param_count}"
            params.append(filters['is_active'])
            param_count += 1
        
        if 'is_budget' in filters:
            query += f" AND s.isbudget = ${param_count}"
            params.append(filters['is_budget'])
            param_count += 1
        
        if 'year' in filters:
            query += f" AND s.year = ${param_count}"
            params.append(filters['year'])
            param_count += 1
        
        if 'search' in filters:
            query += f" AND s.fullname ILIKE ${param_count}"
            params.append(f"%{filters['search']}%")
            param_count += 1
        
        # Добавляем пагинацию
        query += f" ORDER BY s.fullname LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, offset])
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            students = []
            
            for row in rows:
                student_data = dict(row)
                
                # Обрабатываем данные студента
                if student_data['dataid']:
                    student_data['student_data'] = StudentData(
                        id=student_data['dataid'],
                        phone=student_data.pop('phone'),
                        email=student_data.pop('email'),
                        birthday=student_data.pop('birthday'),
                        created_at=student_data['created_at'],
                        updated_at=student_data['updated_at']
                    )
                else:
                    student_data.pop('phone', None)
                    student_data.pop('email', None)
                    student_data.pop('birthday', None)
                    student_data['student_data'] = None
                
                # Получаем статусы
                statuses = await self._get_student_statuses(row['id'], connection)
                student_data['additional_statuses'] = statuses
                
                students.append(Student(**student_data))
            
            return students
    
    async def _get_student_statuses(self, student_id: int, conn: Connection) -> List[AdditionalStatus]:
        """Получить дополнительные статусы студента"""
        query = """
            SELECT a.* FROM additionalstatuses a
            JOIN studentadditionalstatuses sas ON sas.statusid = a.id
            WHERE sas.studentid = $1
        """
        rows = await conn.fetch(query, student_id)
        return [AdditionalStatus(**dict(row)) for row in rows]

    async def count(self, filters: Optional[Dict[str, Any]] = None, conn: Optional[Connection] = None) -> int:
        """Подсчитать количество студентов с учетом фильтров"""
        query = """
            SELECT COUNT(*) FROM students s
            JOIN groups g ON g.id = s.groupid
            WHERE 1=1
        """
        
        params = []
        param_count = 1
        
        if filters:
            if 'group_id' in filters:
                query += f" AND s.groupid = ${param_count}"
                params.append(filters['group_id'])
                param_count += 1
            
            if 'subdivision_id' in filters:
                query += f" AND g.subdivisionid = ${param_count}"
                params.append(filters['subdivision_id'])
                param_count += 1
            
            if 'is_active' in filters:
                query += f" AND s.isactive = ${param_count}"
                params.append(filters['is_active'])
                param_count += 1
            
            if 'is_budget' in filters:
                query += f" AND s.isbudget = ${param_count}"
                params.append(filters['is_budget'])
                param_count += 1
            
            if 'year' in filters:
                query += f" AND s.year = ${param_count}"
                params.append(filters['year'])
                param_count += 1
            
            if 'search' in filters:
                query += f" AND s.fullname ILIKE ${param_count}"
                params.append(f"%{filters['search']}%")
                param_count += 1
        
        async with self._get_connection(conn) as connection:
            return await connection.fetchval(query, *params)