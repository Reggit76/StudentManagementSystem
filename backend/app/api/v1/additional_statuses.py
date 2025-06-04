from typing import List
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from ...models.additional_status import (
    AdditionalStatus, AdditionalStatusCreate, AdditionalStatusUpdate
)
from ...models.common import SuccessResponse
from ...core.exceptions import NotFoundError, AlreadyExistsError
from ..deps import (
    AdditionalStatusRepo, CurrentUser, CSRFProtection, require_roles
)

router = APIRouter(prefix="/additional-statuses", tags=["additional-statuses"])


@router.get("", response_model=List[AdditionalStatus])
async def get_additional_statuses(
    current_user: CurrentUser,
    repo: AdditionalStatusRepo
):
    """Получить список всех дополнительных статусов."""
    return await repo.get_all(order_by="name")


@router.get("/{status_id}", response_model=AdditionalStatus)
async def get_additional_status(
    status_id: int,
    current_user: CurrentUser,
    repo: AdditionalStatusRepo
):
    """Получить дополнительный статус по ID."""
    status = await repo.get_by_id(status_id)
    if not status:
        raise NotFoundError(f"Статус с ID {status_id} не найден")
    return status


@router.post("", response_model=AdditionalStatus, status_code=status.HTTP_201_CREATED)
async def create_additional_status(
    data: AdditionalStatusCreate,
    _: CSRFProtection,
    repo: AdditionalStatusRepo,
    current_user: CurrentUser = require_roles(["Администратор", "Модератор"])
):
    """
    Создать новый дополнительный статус.
    
    Требуется роль: Администратор или Модератор
    """
    # Проверяем уникальность имени
    existing = await repo.get_by_name(data.name)
    if existing:
        raise AlreadyExistsError(f"Статус с названием '{data.name}' уже существует")
    
    try:
        status = await repo.create(data)
        logger.info(f"User {current_user.id} created additional status {status.id}")
        return status
    except Exception as e:
        logger.error(f"Error creating additional status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании статуса"
        )


@router.put("/{status_id}", response_model=AdditionalStatus)
async def update_additional_status(
    status_id: int,
    data: AdditionalStatusUpdate,
    _: CSRFProtection,
    repo: AdditionalStatusRepo,
    current_user: CurrentUser = require_roles(["Администратор", "Модератор"])
):
    """
    Обновить дополнительный статус.
    
    Требуется роль: Администратор или Модератор
    """
    # Проверяем существование
    existing = await repo.get_by_id(status_id)
    if not existing:
        raise NotFoundError(f"Статус с ID {status_id} не найден")
    
    # Проверяем уникальность нового имени
    if data.name and data.name != existing.name:
        duplicate = await repo.get_by_name(data.name)
        if duplicate:
            raise AlreadyExistsError(f"Статус с названием '{data.name}' уже существует")
    
    try:
        status = await repo.update(status_id, data)
        logger.info(f"User {current_user.id} updated additional status {status_id}")
        return status
    except Exception as e:
        logger.error(f"Error updating additional status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении статуса"
        )


@router.delete("/{status_id}", response_model=SuccessResponse)
async def delete_additional_status(
    status_id: int,
    _: CSRFProtection,
    repo: AdditionalStatusRepo,
    current_user: CurrentUser = require_roles(["Администратор"])
):
    """
    Удалить дополнительный статус.
    
    Требуется роль: Администратор
    """
    # Проверяем существование
    existing = await repo.get_by_id(status_id)
    if not existing:
        raise NotFoundError(f"Статус с ID {status_id} не найден")
    
    try:
        success = await repo.delete(status_id)
        if success:
            logger.info(f"User {current_user.id} deleted additional status {status_id}")
            return SuccessResponse(message="Статус успешно удален")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении статуса"
            )
    except Exception as e:
        logger.error(f"Error deleting additional status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении статуса"
        )