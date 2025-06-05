# backend/app/models/contribution.py

from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class ContributionBase(BaseModel):
    """Базовая модель взноса"""
    studentid: int = Field(..., description="ID студента")
    semester: int = Field(..., ge=1, le=2, description="Семестр")
    amount: Decimal = Field(..., ge=Decimal('0'), lt=Decimal('100000'), description="Сумма взноса")
    paymentdate: Optional[date] = Field(None, description="Дата оплаты")
    year: int = Field(
        default_factory=lambda: date.today().year,
        ge=2000,
        le=2100,
        description="Год взноса"
    )

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }

    @field_validator('paymentdate')
    @classmethod
    def validate_payment_date(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError('Дата оплаты не может быть в будущем')
        return v


class Contribution(BaseDBModel, ContributionBase):
    """Модель взноса из БД"""
    student_name: Optional[str] = Field(None, description="ФИО студента")
    group_name: Optional[str] = Field(None, description="Название группы")


class ContributionCreate(BaseCreateModel, ContributionBase):
    """Модель для создания взноса"""
    pass


class ContributionUpdate(BaseUpdateModel):
    """Модель для обновления взноса"""
    semester: Optional[int] = Field(None, ge=1, le=2, description="Семестр")
    amount: Optional[Decimal] = Field(None, ge=Decimal('0'), lt=Decimal('100000'), description="Сумма взноса")
    paymentdate: Optional[date] = Field(None, description="Дата оплаты")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="Год взноса")


class ContributionSummary(BaseModel):
    """Модель сводки по взносам"""
    year: int = Field(..., description="Год")
    semester: int = Field(..., description="Семестр")
    total_amount: Decimal = Field(..., description="Общая сумма")
    paid_count: int = Field(..., description="Количество оплаченных")
    unpaid_count: int = Field(..., description="Количество неоплаченных")
    total_students: int = Field(..., description="Общее количество студентов")