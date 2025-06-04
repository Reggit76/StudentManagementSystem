from typing import List, Optional
from decimal import Decimal
from datetime import date
from fastapi import APIRouter, HTTPException, status, Query
from loguru import logger

from ...models.contribution import (
    Contribution, ContributionCreate, ContributionUpdate, ContributionSummary
)
from ...models.common import PaginatedResponse, SuccessResponse
from ...core.exceptions import NotFoundError, ValidationError, AuthorizationError
from ...utils.permissions import PermissionChecker
from ..deps import (
    ContributionRepo, StudentRepo, GroupRepo,
    CurrentUser, CSRFProtection, PaginationParams
)

router = APIRouter(prefix="/contributions", tags=["contributions"])


@router.get("", response_model=PaginatedResponse[Contribution])
async def get_contributions(
    pagination: PaginationParams,
    current_user: CurrentUser,
    repo: ContributionRepo,
    student_id: Optional[int] = Query(None, description="Фильтр по студенту"),
    group_id: Optional[int] = Query(None, description="Фильтр по группе"),
    year: Optional[int] = Query(None, description="Фильтр по году"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="Фильтр по семестру"),
    paid_only: Optional[bool] = Query(None, description="Только оплаченные")
):
    """
    Получить список взносов с фильтрацией.
    
    Фильтры:
    - **student_id**: ID студента
    - **group_id**: ID группы  
    - **year**: год взноса
    - **semester**: семестр (1 или 2)
    - **paid_only**: только оплаченные взносы
    """
    # Формируем фильтры
    filters = {}
    if student_id:
        filters['student_id'] = student_id
    if year:
        filters['year'] = year
    if semester:
        filters['semester'] = semester
    if paid_only is not None:
        if paid_only:
            filters['payment_date_not_null'] = True
        else:
            filters['payment_date_null'] = True
    
    # Получаем данные с пагинацией
    offset = (pagination.page - 1) * pagination.size
    
    if group_id:
        items = await repo.get_by_group(
            group_id=group_id,
            year=year or date.today().year,
            semester=semester
        )
        # Применяем пагинацию вручную
        total = len(items)
        items = items[offset:offset + pagination.size]
    else:
        # TODO: Реализовать общий поиск с фильтрами
        items = []
        total = 0
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


@router.get("/summary", response_model=ContributionSummary)
async def get_contributions_summary(
    current_user: CurrentUser,
    repo: ContributionRepo,
    year: int = Query(..., description="Год для сводки"),
    semester: int = Query(..., ge=1, le=2, description="Семестр"),
    subdivision_id: Optional[int] = Query(None, description="Фильтр по подразделению")
):
    """
    Получить сводку по взносам за период.
    """
    # Применяем ограничения по подразделению
    filter_subdivision_id = PermissionChecker.filter_by_subdivision(
        current_user, subdivision_id
    )
    
    summary = await repo.get_summary(
        year=year,
        semester=semester,
        subdivision_id=filter_subdivision_id
    )
    
    return summary


@router.get("/{contribution_id}", response_model=Contribution)
async def get_contribution(
    contribution_id: int,
    current_user: CurrentUser,
    repo: ContributionRepo
):
    """Получить взнос по ID."""
    contribution = await repo.get_with_details(contribution_id)
    if not contribution:
        raise NotFoundError(f"Взнос с ID {contribution_id} не найден")
    
    return contribution


@router.post("", response_model=Contribution, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    data: ContributionCreate,
    _: CSRFProtection,
    repo: ContributionRepo,
    student_repo: StudentRepo,
    group_repo: GroupRepo,
    current_user: CurrentUser
):
    """
    Создать новый взнос.
    
    Требуется роль: Администратор, Модератор или Оператор
    """
    # Проверяем существование студента
    student = await student_repo.get_by_id(data.student_id)
    if not student:
        raise NotFoundError(f"Студент с ID {data.student_id} не найден")
    
    # Проверяем права через группу студента
    group = await group_repo.get_by_id(student.group_id)
    if not PermissionChecker.can_manage_contributions(current_user, group.subdivision_id):
        raise AuthorizationError("Недостаточно прав для создания взноса")
    
    try:
        contribution = await repo.create(data)
        logger.info(f"User {current_user.id} created contribution {contribution.id}")
        return contribution
    except Exception as e:
        logger.error(f"Error creating contribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании взноса"
        )


@router.put("/{contribution_id}", response_model=Contribution)
async def update_contribution(
    contribution_id: int,
    data: ContributionUpdate,
    _: CSRFProtection,
    repo: ContributionRepo,
    current_user: CurrentUser
):
    """
    Обновить взнос.
    
    Требуется роль: Администратор, Модератор или Оператор
    """
    # Получаем существующий взнос
    existing = await repo.get_with_details(contribution_id)
    if not existing:
        raise NotFoundError(f"Взнос с ID {contribution_id} не найден")
    
    # TODO: Добавить проверку прав через студента
    
    try:
        contribution = await repo.update(contribution_id, data)
        logger.info(f"User {current_user.id} updated contribution {contribution_id}")
        return contribution
    except Exception as e:
        logger.error(f"Error updating contribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении взноса"
        )


@router.delete("/{contribution_id}", response_model=SuccessResponse)
async def delete_contribution(
    contribution_id: int,
    _: CSRFProtection,
    repo: ContributionRepo,
    current_user: CurrentUser
):
    """
    Удалить взнос.
    
    Требуется роль: Администратор или Модератор
    """
    # Получаем взнос
    contribution = await repo.get_with_details(contribution_id)
    if not contribution:
        raise NotFoundError(f"Взнос с ID {contribution_id} не найден")
    
    # Проверяем права на удаление
    if not PermissionChecker.has_permission(current_user, "delete_all"):
        raise AuthorizationError("Недостаточно прав для удаления взноса")
    
    try:
        success = await repo.delete(contribution_id)
        if success:
            logger.info(f"User {current_user.id} deleted contribution {contribution_id}")
            return SuccessResponse(message="Взнос успешно удален")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении взноса"
            )
    except Exception as e:
        logger.error(f"Error deleting contribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении взноса"
        )


@router.post("/mark-paid/{student_id}", response_model=Contribution)
async def mark_contribution_as_paid(
    student_id: int,
    _: CSRFProtection,
    repo: ContributionRepo,
    current_user: CurrentUser,
    year: int = Query(..., description="Год взноса"),
    semester: int = Query(..., ge=1, le=2, description="Семестр"),
    amount: Decimal = Query(..., description="Сумма взноса"),
    payment_date: Optional[date] = Query(None, description="Дата платежа")
):
    """
    Отметить взнос как оплаченный.
    """
    if not payment_date:
        payment_date = date.today()
    
    try:
        contribution = await repo.mark_as_paid(
            student_id=student_id,
            year=year,
            semester=semester,
            amount=amount,
            payment_date=payment_date
        )
        logger.info(f"User {current_user.id} marked contribution as paid for student {student_id}")
        return contribution
    except Exception as e:
        logger.error(f"Error marking contribution as paid: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отметке взноса как оплаченного"
        )