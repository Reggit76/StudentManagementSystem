from typing import Optional, List
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel
from .role import Role


class UserBase(BaseModel):
    login: str = Field(..., description="Логин пользователя")
    subdivision_id: Optional[int] = Field(None, description="ID подразделения")


class User(BaseDBModel, UserBase):
    """Модель пользователя из БД"""
    roles: List[Role] = Field(default_factory=list, description="Роли пользователя")
    subdivision_name: Optional[str] = Field(None, description="Название подразделения")


class UserCreate(BaseCreateModel, UserBase):
    """Модель для создания пользователя"""
    password: str = Field(..., description="Пароль")
    role_ids: List[int] = Field(default_factory=list, description="ID ролей")


class UserUpdate(BaseUpdateModel):
    """Модель для обновления пользователя"""
    login: Optional[str] = None
    password: Optional[str] = None
    subdivision_id: Optional[int] = None
    role_ids: Optional[List[int]] = None


class UserInDB(User):
    """Модель пользователя в БД с хешем пароля"""
    password_hash: str = Field(..., description="Хеш пароля")