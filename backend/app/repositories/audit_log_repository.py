# backend/app/repositories/audit_log_repository.py

from typing import Optional, List, Dict, Any
from datetime import datetime
from asyncpg import Connection
from .base import BaseRepository
from ..models.audit_log import AuditLog, AuditLogCreate, AuditLogFilter


class AuditLogRepository(BaseRepository[AuditLog]):
    """Репозиторий для работы с логами аудита"""
    
    @property
    def table_name(self) -> str:
        return "audit_logs"
    
    @property
    def model_class(self):
        return AuditLog
    
    async def create_log(self, data: AuditLogCreate, conn: Optional[Connection] = None) -> AuditLog:
        """Создать запись в логе"""
        query = """
            INSERT INTO audit_logs (
                user_id, action, table_name, record_id, 
                old_data, new_data, ip_address, user_agent
            ) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8) 
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(
                query,
                data.user_id,
                data.action,
                data.table_name,
                data.record_id,
                data.old_data,
                data.new_data,
                data.ip_address,
                data.user_agent
            )
            return await self.get_with_user_info(row['id'], connection)
    
    async def get_with_user_info(self, id: int, conn: Optional[Connection] = None) -> Optional[AuditLog]:
        """Получить лог с информацией о пользователе"""
        query = """
            SELECT 
                al.*,
                u.login as user_login
            FROM audit_logs al
            LEFT JOIN users u ON u.id = al.user_id
            WHERE al.id = $1
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return AuditLog(**dict(row)) if row else None
    
    async def search_logs(
        self,
        filters: AuditLogFilter,
        limit: int = 100,
        offset: int = 0,
        conn: Optional[Connection] = None
    ) -> List[AuditLog]:
        """Поиск логов по фильтрам"""
        query = """
            SELECT 
                al.*,
                u.login as user_login
            FROM audit_logs al
            LEFT JOIN users u ON u.id = al.user_id
            WHERE 1=1
        """
        
        params = []
        param_count = 1
        
        if filters.user_id:
            query += f" AND al.user_id = ${param_count}"
            params.append(filters.user_id)
            param_count += 1
        
        if filters.action:
            query += f" AND al.action = ${param_count}"
            params.append(filters.action)
            param_count += 1
        
        if filters.table_name:
            query += f" AND al.table_name = ${param_count}"
            params.append(filters.table_name)
            param_count += 1
        
        if filters.record_id:
            query += f" AND al.record_id = ${param_count}"
            params.append(filters.record_id)
            param_count += 1
        
        if filters.date_from:
            query += f" AND al.created_at >= ${param_count}"
            params.append(filters.date_from)
            param_count += 1
        
        if filters.date_to:
            query += f" AND al.created_at <= ${param_count}"
            params.append(filters.date_to)
            param_count += 1
        
        query += f" ORDER BY al.created_at DESC LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, offset])
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            return [AuditLog(**dict(row)) for row in rows]
    
    async def count_logs(self, filters: AuditLogFilter, conn: Optional[Connection] = None) -> int:
        """Подсчитать количество логов по фильтрам"""
        query = "SELECT COUNT(*) FROM audit_logs WHERE 1=1"
        
        params = []
        param_count = 1
        
        if filters.user_id:
            query += f" AND user_id = ${param_count}"
            params.append(filters.user_id)
            param_count += 1
        
        if filters.action:
            query += f" AND action = ${param_count}"
            params.append(filters.action)
            param_count += 1
        
        if filters.table_name:
            query += f" AND table_name = ${param_count}"
            params.append(filters.table_name)
            param_count += 1
        
        if filters.record_id:
            query += f" AND record_id = ${param_count}"
            params.append(filters.record_id)
            param_count += 1
        
        if filters.date_from:
            query += f" AND created_at >= ${param_count}"
            params.append(filters.date_from)
            param_count += 1
        
        if filters.date_to:
            query += f" AND created_at <= ${param_count}"
            params.append(filters.date_to)
            param_count += 1
        
        async with self._get_connection(conn) as connection:
            return await connection.fetchval(query, *params)