from typing import Optional
from datetime import date
from pydantic import BaseModel
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


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


class StudentDataBase(BaseModel):
    passport_number: str
    passport_issued_by: str
    passport_issue_date: date
    registration_address: str
    actual_address: str
    birth_place: str
    insurance_number: Optional[str] = None
    tin: Optional[str] = None
    mother_info: Optional[str] = None
    father_info: Optional[str] = None


class StudentData(BaseDBModel, StudentDataBase):
    pass


class StudentDataCreate(BaseCreateModel, StudentDataBase):
    pass


class StudentDataUpdate(BaseUpdateModel):
    passport_number: Optional[str] = None
    passport_issued_by: Optional[str] = None
    passport_issue_date: Optional[date] = None
    registration_address: Optional[str] = None
    actual_address: Optional[str] = None
    birth_place: Optional[str] = None
    insurance_number: Optional[str] = None
    tin: Optional[str] = None
    mother_info: Optional[str] = None
    father_info: Optional[str] = None