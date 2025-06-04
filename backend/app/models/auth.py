from typing import Optional, List
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Модель токена доступа"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из токена"""
    user_id: Optional[int] = None
    login: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    subdivision_id: Optional[int] = None


class UserAuth(BaseModel):
    """Модель для аутентификации"""
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    """Модель для изменения пароля"""
    old_password: str
    new_password: str