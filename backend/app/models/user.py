# backend/app/models/user.py

from typing import Optional, List
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel
from .role import Role


class UserBase(BaseModel):
    """Базовая модель пользователя"""
    login: str = Field(..., description="Логин пользователя")
    subdivisionid: Optional[int] = Field(None, description="ID подразделения", alias="subdivision_id")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }


class User(BaseDBModel, UserBase):
    """Модель пользователя из БД"""
    roles: List[Role] = Field(default_factory=list, description="Роли пользователя")
    subdivision_name: Optional[str] = Field(None, description="Название подразделения")


class UserCreate(BaseCreateModel, UserBase):
    """Модель для создания пользователя"""
    password: str = Field(..., description="Пароль", min_length=6)
    role_ids: List[int] = Field(default_factory=list, description="ID ролей")


class UserUpdate(BaseUpdateModel):
    """Модель для обновления пользователя"""
    login: Optional[str] = Field(None, description="Логин пользователя")
    password: Optional[str] = Field(None, description="Пароль", min_length=6)
    subdivisionid: Optional[int] = Field(None, description="ID подразделения", alias="subdivision_id")
    role_ids: Optional[List[int]] = Field(None, description="ID ролей")


class UserInDB(User):
    """Модель пользователя в БД с хешем пароля"""
    passwordhash: str = Field(..., description="Хеш пароля", alias="password_hash")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }