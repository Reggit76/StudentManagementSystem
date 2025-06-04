from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseDBModel, BaseCreateModel, BaseUpdateModel


class ContributionBase(BaseModel):
    """Базовая модель взноса"""
    student_id: int
    semester: int = Field(ge=1, le=2)
    amount: Decimal = Field(ge=Decimal('0'), lt=Decimal('100000'))
    payment_date: Optional[date] = None
    year: int = Field(
        default_factory=lambda: date.today().year,
        ge=2000,
        le=2100
    )

    def validate_payment_date(self, value: Optional[date]) -> Optional[date]:
        if value and value > date.today():
            raise ValueError('Дата оплаты не может быть в будущем')
        return value


class Contribution(BaseDBModel, ContributionBase):
    """Модель взноса из БД"""
    id: int
    student_name: Optional[str] = None
    group_name: Optional[str] = None


class ContributionCreate(BaseCreateModel, ContributionBase):
    """Модель для создания взноса"""
    pass


class ContributionUpdate(BaseUpdateModel):
    """Модель для обновления взноса"""
    semester: Optional[int] = Field(None, ge=1, le=2)
    amount: Optional[Decimal] = Field(None, ge=Decimal('0'), lt=Decimal('100000'))
    payment_date: Optional[date] = None
    year: Optional[int] = Field(None, ge=2000, le=2100)


class ContributionSummary(BaseDBModel):
    """Модель сводки по взносам"""
    year: int
    semester: int
    total_amount: Decimal
    paid_count: int
    unpaid_count: int
    total_students: int