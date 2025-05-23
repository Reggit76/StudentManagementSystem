from typing import Optional, List
from pydantic import Field, field_validator
from .base import BaseDBModel
from .role import Role


class UserBase(BaseDBModel):
    """Базовая модель пользователя"""
    login: str = Field(..., min_length=3, max_length=50, description="Логин пользователя")
    subdivision_id: Optional[int] = Field(None, gt=0, description="ID подразделения")

    @field_validator('login')
    @classmethod
    def validate_login(cls, v):
        if not v or not v.strip():
            raise ValueError('Логин не может быть пустым')
        # Проверка на допустимые символы в логине
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Логин может содержать только латинские буквы, цифры, дефис и подчеркивание')
        return v.strip().lower()


class UserCreate(UserBase):
    """Модель для создания пользователя"""
    password: str = Field(..., min_length=8, description="Пароль")
    role_ids: List[int] = Field(default_factory=list, description="Список ID ролей")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        # Проверка сложности пароля
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.islower() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class UserUpdate(BaseDBModel):
    """Модель для обновления пользователя"""
    subdivision_id: Optional[int] = Field(None, gt=0)
    password: Optional[str] = Field(None, min_length=8)
    role_ids: Optional[List[int]] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.islower() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class User(UserBase):
    """Модель пользователя из БД"""
    id: int
    roles: List[Role] = []
    subdivision_name: Optional[str] = None


class UserInDB(User):
    """Модель пользователя в БД с хешем пароля"""
    password_hash: str