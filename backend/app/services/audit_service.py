# backend/app/services/audit_service.py

from typing import Optional, Dict, Any
from fastapi import Request
from loguru import logger

from ..models.audit_log import AuditLogCreate
from ..repositories.audit_log_repository import AuditLogRepository
from ..core.database import db


class AuditService:
    """Сервис для логирования действий пользователей"""
    
    @staticmethod
    async def log_action(
        user_id: Optional[int],
        action: str,
        table_name: str,
        record_id: Optional[int] = None,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Записать действие в лог"""
        try:
            pool = await db.get_pool()
            repo = AuditLogRepository(pool)
            
            # Получаем информацию о запросе
            ip_address = None
            user_agent = None
            
            if request:
                # Получаем IP адрес
                forwarded_for = request.headers.get("X-Forwarded-For")
                if forwarded_for:
                    ip_address = forwarded_for.split(",")[0].strip()
                else:
                    ip_address = str(request.client.host) if request.client else None
                
                # Получаем User Agent
                user_agent = request.headers.get("User-Agent")
            
            # Сериализуем данные в JSON
            import json
            old_data_json = json.dumps(old_data, default=str) if old_data else None
            new_data_json = json.dumps(new_data, default=str) if new_data else None
            
            log_data = AuditLogCreate(
                user_id=user_id,
                action=action,
                table_name=table_name,
                record_id=record_id,
                old_data=old_data_json,
                new_data=new_data_json,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            await repo.create_log(log_data)
            
        except Exception as e:
            # Логируем ошибку, но не прерываем основную операцию
            logger.error(f"Failed to log audit action: {e}")
    
    @staticmethod
    async def log_create(
        user_id: Optional[int],
        table_name: str,
        record_id: int,
        data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Логировать создание записи"""
        await AuditService.log_action(
            user_id=user_id,
            action="CREATE",
            table_name=table_name,
            record_id=record_id,
            new_data=data,
            request=request
        )
    
    @staticmethod
    async def log_update(
        user_id: Optional[int],
        table_name: str,
        record_id: int,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Логировать обновление записи"""
        await AuditService.log_action(
            user_id=user_id,
            action="UPDATE",
            table_name=table_name,
            record_id=record_id,
            old_data=old_data,
            new_data=new_data,
            request=request
        )
    
    @staticmethod
    async def log_delete(
        user_id: Optional[int],
        table_name: str,
        record_id: int,
        data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Логировать удаление записи"""
        await AuditService.log_action(
            user_id=user_id,
            action="DELETE",
            table_name=table_name,
            record_id=record_id,
            old_data=data,
            request=request
        )