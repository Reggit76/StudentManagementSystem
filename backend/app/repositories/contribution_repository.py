from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from asyncpg import Connection
from .base import BaseRepository
from ..models.contribution import Contribution, ContributionCreate, ContributionUpdate, ContributionSummary


class ContributionRepository(BaseRepository[Contribution]):
    """Репозиторий для работы со взносами"""
    
    @property
    def table_name(self) -> str:
        return "contributions"
    
    @property
    def model_class(self):
        return Contribution
    
    async def create(self, data: ContributionCreate, conn: Optional[Connection] = None) -> Contribution:
        """Создать взнос"""
        query = """
            INSERT INTO contributions (studentid, semester, amount, paymentdate, year) 
            VALUES ($1, $2, $3, $4, $5) 
            ON CONFLICT (studentid, year) DO UPDATE
            SET semester = EXCLUDED.semester,
                amount = EXCLUDED.amount,
                paymentdate = EXCLUDED.paymentdate
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(
                query,
                data.studentid,
                data.semester,
                data.amount,
                data.paymentdate,
                data.year
            )
            return await self.get_with_details(row['id'], connection)
    
    async def update(self, id: int, data: ContributionUpdate, conn: Optional[Connection] = None) -> Optional[Contribution]:
        """Обновить взнос"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_with_details(id, conn)
        
        # Маппинг имен полей
        field_mapping = {
            'payment_date': 'paymentdate'
        }
        
        set_parts = []
        values = [id]
        for i, (field, value) in enumerate(update_data.items()):
            db_field = field_mapping.get(field, field)
            set_parts.append(f"{db_field} = ${i+2}")
            values.append(value)
        
        query = f"""
            UPDATE contributions 
            SET {', '.join(set_parts)}
            WHERE id = $1
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *values)
            return await self.get_with_details(row['id'], connection) if row else None
    
    async def get_with_details(self, id: int, conn: Optional[Connection] = None) -> Optional[Contribution]:
        """Получить взнос с деталями"""
        query = """
            SELECT 
                c.*,
                s.fullname as student_name,
                g.name as group_name
            FROM contributions c
            JOIN students s ON s.id = c.studentid
            JOIN groups g ON g.id = s.groupid
            WHERE c.id = $1
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return Contribution(**dict(row)) if row else None
    
    async def get_by_student(self, student_id: int, year: Optional[int] = None, conn: Optional[Connection] = None) -> List[Contribution]:
        """Получить взносы студента"""
        if year:
            query = """
                SELECT c.* FROM contributions c
                WHERE c.studentid = $1 AND c.year = $2
                ORDER BY c.year DESC, c.semester DESC
            """
            params = [student_id, year]
        else:
            query = """
                SELECT c.* FROM contributions c
                WHERE c.studentid = $1
                ORDER BY c.year DESC, c.semester DESC
            """
            params = [student_id]
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [Contribution(**dict(row)) for row in rows]
    
    async def get_by_group(
        self, 
        group_id: int, 
        year: int, 
        semester: Optional[int] = None,
        conn: Optional[Connection] = None
    ) -> List[Contribution]:
        """Получить взносы группы"""
        base_query = """
            SELECT 
                c.*,
                s.fullname as student_name
            FROM contributions c
            JOIN students s ON s.id = c.studentid
            WHERE s.groupid = $1 AND c.year = $2
        """
        
        if semester:
            query = base_query + " AND c.semester = $3 ORDER BY s.fullname"
            params = [group_id, year, semester]
        else:
            query = base_query + " ORDER BY s.fullname"
            params = [group_id, year]
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [Contribution(**dict(row)) for row in rows]
    
    async def get_unpaid_students(
        self, 
        group_id: int, 
        year: int, 
        semester: int,
        conn: Optional[Connection] = None
    ) -> List[Dict[str, Any]]:
        """Получить студентов без взносов"""
        query = """
            SELECT 
                s.id,
                s.fullname,
                s.isactive,
                s.isbudget
            FROM students s
            WHERE s.groupid = $1
            AND s.year = $2
            AND NOT EXISTS (
                SELECT 1 FROM contributions c
                WHERE c.studentid = s.id
                AND c.year = $2
                AND c.semester = $3
                AND c.paymentdate IS NOT NULL
            )
            ORDER BY s.fullname
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, group_id, year, semester)
            return [dict(row) for row in rows]
    
    async def get_summary(
        self, 
        year: int, 
        semester: int,
        subdivision_id: Optional[int] = None,
        conn: Optional[Connection] = None
    ) -> ContributionSummary:
        """Получить сводку по взносам"""
        base_query = """
            SELECT 
                COUNT(DISTINCT s.id) as total_students,
                COUNT(DISTINCT c.studentid) FILTER (WHERE c.paymentdate IS NOT NULL) as paid_count,
                COUNT(DISTINCT s.id) - COUNT(DISTINCT c.studentid) FILTER (WHERE c.paymentdate IS NOT NULL) as unpaid_count,
                COALESCE(SUM(c.amount) FILTER (WHERE c.paymentdate IS NOT NULL), 0) as total_amount
            FROM students s
            JOIN groups g ON g.id = s.groupid
            LEFT JOIN contributions c ON c.studentid = s.id AND c.year = $1 AND c.semester = $2
            WHERE s.year = $1
        """
        
        if subdivision_id:
            query = base_query + " AND g.subdivisionid = $3"
            params = [year, semester, subdivision_id]
        else:
            query = base_query
            params = [year, semester]
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, *params)
            return ContributionSummary(
                year=year,
                semester=semester,
                total_students=row['total_students'],
                paid_count=row['paid_count'],
                unpaid_count=row['unpaid_count'],
                total_amount=row['total_amount']
            )
    
    async def mark_as_paid(
        self, 
        student_id: int, 
        year: int, 
        semester: int,
        amount: Decimal,
        payment_date: Optional[date] = None,
        conn: Optional[Connection] = None
    ) -> Contribution:
        """Отметить взнос как оплаченный"""
        if not payment_date:
            payment_date = date.today()
        
        query = """
            INSERT INTO contributions (studentid, semester, amount, paymentdate, year) 
            VALUES ($1, $2, $3, $4, $5) 
            ON CONFLICT (studentid, year) DO UPDATE
            SET semester = EXCLUDED.semester,
                amount = EXCLUDED.amount,
                paymentdate = EXCLUDED.paymentdate
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(
                query,
                student_id,
                semester,
                amount,
                payment_date,
                year
            )
            return await self.get_with_details(row['id'], connection)