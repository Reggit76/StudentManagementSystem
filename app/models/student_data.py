from pydantic import Field
from .base import BaseDBModel


class UserRoleBase(BaseDBModel):
    """Базовая модель связи пользователь-роль"""
    user_id: int = Field(..., gt=0, description="ID пользователя")
    role_id: int = Field(..., gt=0, description="ID роли")


class UserRoleCreate(UserRoleBase):
    """Модель для создания связи пользователь-роль"""
    pass


class UserRole(UserRoleBase):
    """Модель связи пользователь-роль из БД"""
    pass