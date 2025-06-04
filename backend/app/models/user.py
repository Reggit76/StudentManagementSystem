from typing import Optional, List
from pydantic import EmailStr, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel
from .role import Role


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    is_active: bool = True


class User(BaseDBModel, UserBase):
    hashed_password: str
    roles: List[Role] = []


class UserCreate(BaseCreateModel, UserBase):
    password: str
    roles: List[int] = []


class UserUpdate(BaseUpdateModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[int]] = None


class UserInDB(User):
    pass