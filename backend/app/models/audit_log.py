# backend/app/models/audit_log.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .base import BaseDBModel


class AuditLogBase(BaseModel):
    """Базовая модель лога аудита"""
    user_id: Optional[int] = Field(None, description="ID пользователя")
    action: str = Field(..., description="Действие (CREATE, UPDATE, DELETE, VIEW)")
    table_name: str = Field(..., description="Название таблицы")
    record_id: Optional[int] = Field(None, description="ID записи")
    old_data: Optional[str] = Field(None, description="Старые данные (JSON)")
    new_data: Optional[str] = Field(None, description="Новые данные (JSON)")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent")


class AuditLog(BaseDBModel, AuditLogBase):
    """Модель лога аудита из БД"""
    user_login: Optional[str] = Field(None, description="Логин пользователя")


class AuditLogCreate(BaseModel):
    """Модель для создания лога аудита"""
    user_id: Optional[int] = None
    action: str
    table_name: str
    record_id: Optional[int] = None
    old_data: Optional[str] = None
    new_data: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogFilter(BaseModel):
    """Фильтры для поиска логов"""
    user_id: Optional[int] = None
    action: Optional[str] = None
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None