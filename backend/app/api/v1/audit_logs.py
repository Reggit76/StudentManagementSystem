from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, status
from loguru import logger

from ...models.audit_log import AuditLog, AuditLogFilter
from ...models.common import PaginatedResponse
from ...utils.permissions import PermissionChecker
from ..deps import CurrentUser, PaginationParams
from ...repositories.audit_log_repository import AuditLogRepository
from ...core.database import db

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=PaginatedResponse[AuditLog])
async def get_audit_logs(
    pagination: PaginationParams,
    current_user: CurrentUser,
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    action: Optional[str] = Query(None, description="Фильтр по действию"),
    table_name: Optional[str] = Query(None, description="Фильтр по таблице"),
    record_id: Optional[int] = Query(None, description="Фильтр по ID записи"),
    date_from: Optional[datetime] = Query(None, description="Дата начала"),
    date_to: Optional[datetime] = Query(None, description="Дата окончания")
):
    """
    Получить логи аудита.
    
    Требуется роль: CHAIRMAN
    """
    # Проверяем права доступа - только председатель может смотреть логи
    if not PermissionChecker.has_permission(current_user, "view_all"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра логов аудита"
        )
    
    try:
        pool = await db.get_pool()
        repo = AuditLogRepository(pool)
        
        # Формируем фильтры
        filters = AuditLogFilter(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Получаем данные
        offset = (pagination.page - 1) * pagination.size
        logs = await repo.search_logs(filters, limit=pagination.size, offset=offset)
        total = await repo.count_logs(filters)
        
        return PaginatedResponse(
            items=logs,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении логов аудита"
        )


@router.get("/actions", response_model=List[str])
async def get_available_actions(current_user: CurrentUser):
    """Получить список доступных действий для фильтрации"""
    if not PermissionChecker.has_permission(current_user, "view_all"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    return ["CREATE", "UPDATE", "DELETE", "VIEW"]


@router.get("/tables", response_model=List[str])
async def get_available_tables(current_user: CurrentUser):
    """Получить список таблиц для фильтрации"""
    if not PermissionChecker.has_permission(current_user, "view_all"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    return [
        "users", "roles", "subdivisions", "groups", 
        "students", "studentdata", "contributions", 
        "hostelstudents", "additionalstatuses"
    ]