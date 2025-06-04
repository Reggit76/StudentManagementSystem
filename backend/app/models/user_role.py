from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class UserRoleBase(BaseModel):
    """Базовая модель связи пользователь-роль"""
    user_id: int
    role_id: int


class UserRole(BaseDBModel, UserRoleBase):
    """Модель связи пользователь-роль из БД"""
    pass


class UserRoleCreate(BaseCreateModel, UserRoleBase):
    """Модель для создания связи пользователь-роль"""
    pass


class UserRoleUpdate(BaseUpdateModel):
    user_id: Optional[int] = None
    role_id: Optional[int] = None