from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import Field, field_validator
from .base import BaseDBModel


class ContributionBase(BaseDBModel):
    """Базовая модель взноса"""
    student_id: int = Field(..., gt=0, description="ID студента")
    semester: int = Field(..., ge=1, le=2, description="Семестр (1 или 2)")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Сумма взноса")
    payment_date: Optional[date] = Field(None, description="Дата оплаты")
    year: int = Field(default_factory=lambda: datetime.now().year, ge=2000, le=2100)

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Сумма взноса должна быть положительной')
        if v > Decimal('100000'):  # Максимальная сумма взноса
            raise ValueError('Сумма взноса слишком большая')
        return v

    @field_validator('payment_date')
    @classmethod
    def validate_payment_date(cls, v):
        if v is None:
            return v
        if v > date.today():
            raise ValueError('Дата оплаты не может быть в будущем')
        return v


class ContributionCreate(ContributionBase):
    """Модель для создания взноса"""
    pass


class ContributionUpdate(BaseDBModel):
    """Модель для обновления взноса"""
    semester: Optional[int] = Field(None, ge=1, le=2)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    payment_date: Optional[date] = None
    year: Optional[int] = Field(None, ge=2000, le=2100)

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Сумма взноса должна быть положительной')
        if v is not None and v > Decimal('100000'):
            raise ValueError('Сумма взноса слишком большая')
        return v

    @field_validator('payment_date')
    @classmethod
    def validate_payment_date(cls, v):
        if v is not None and v > date.today():
            raise ValueError('Дата оплаты не может быть в будущем')
        return v


class Contribution(ContributionBase):
    """Модель взноса из БД"""
    id: int
    student_name: Optional[str] = None
    group_name: Optional[str] = None


class ContributionSummary(BaseDBModel):
    """Модель сводки по взносам"""
    year: int
    semester: int
    total_amount: Decimal
    paid_count: int
    unpaid_count: int
    total_students: int