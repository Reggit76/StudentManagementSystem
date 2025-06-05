from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from loguru import logger

from ...models.subdivision import (
    Subdivision, SubdivisionCreate, SubdivisionUpdate, SubdivisionWithStats
)
from ...models.common import PaginatedResponse, SuccessResponse
from ...core.exceptions import NotFoundError, AlreadyExistsError
from ..deps import (
    SubdivisionRepo, CurrentUser, CSRFProtection, PaginationParams,
    require_roles
)

router = APIRouter(prefix="/subdivisions", tags=["subdivisions"])

@router.get("/list", response_model=List[Subdivision])
async def get_subdivisions_list(
    current_user: CurrentUser,
    repo: SubdivisionRepo
):
    """
    Получить простой список всех подразделений (без пагинации).
    Используется фронтендом для простого отображения.
    """
    try:
        # Получаем все подразделения
        items = await repo.get_all(limit=1000, offset=0, order_by="name")
        return items
    except Exception as e:
        logger.error(f"Error getting subdivisions list: {e}")
        return []


@router.get("", response_model=PaginatedResponse[Subdivision])
async def get_subdivisions(
    pagination: PaginationParams,
    current_user: CurrentUser,
    repo: SubdivisionRepo,
    search: Optional[str] = Query(None, description="Поиск по названию")
):
    """
    Получить список подразделений с пагинацией.
    
    - **page**: номер страницы (по умолчанию 1)
    - **size**: размер страницы (по умолчанию 50, максимум 100)
    - **search**: поиск по названию
    """
    # Получаем общее количество
    filters = {}
    if search:
        # Для поиска используем ILIKE в репозитории
        filters['name_search'] = search
    
    total = await repo.count(filters)
    
    # Получаем данные с пагинацией
    offset = (pagination.page - 1) * pagination.size
    items = await repo.get_all(
        limit=pagination.size,
        offset=offset,
        order_by=pagination.sort_by or "name",
        order_desc=(pagination.sort_order == "desc")
    )
    
    # Фильтруем по поиску если нужно (так как базовый get_all не поддерживает поиск)
    if search:
        items = [item for item in items if search.lower() in item.name.lower()]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


@router.get("/with-stats", response_model=List[SubdivisionWithStats])
async def get_subdivisions_with_stats(
    current_user: CurrentUser,
    repo: SubdivisionRepo
):
    """
    Получить все подразделения со статистикой.
    
    Возвращает список подразделений с количеством:
    - групп
    - студентов  
    - пользователей
    """
    return await repo.get_all_with_stats()


@router.get("/{subdivision_id}", response_model=Subdivision)
async def get_subdivision(
    subdivision_id: int,
    current_user: CurrentUser,
    repo: SubdivisionRepo
):
    """Получить подразделение по ID."""
    subdivision = await repo.get_by_id(subdivision_id)
    if not subdivision:
        raise NotFoundError(f"Подразделение с ID {subdivision_id} не найдено")
    return subdivision


@router.get("/{subdivision_id}/stats", response_model=SubdivisionWithStats)
async def get_subdivision_stats(
    subdivision_id: int,
    current_user: CurrentUser,
    repo: SubdivisionRepo
):
    """Получить подразделение со статистикой."""
    subdivision = await repo.get_with_stats(subdivision_id)
    if not subdivision:
        raise NotFoundError(f"Подразделение с ID {subdivision_id} не найдено")
    return subdivision


@router.post("", response_model=Subdivision, status_code=status.HTTP_201_CREATED)
async def create_subdivision(
    data: SubdivisionCreate,
    _: CSRFProtection,
    repo: SubdivisionRepo,
    current_user: CurrentUser = require_roles(["CHAIRMAN"])
):
    """
    Создать новое подразделение.
    
    Требуется роль: CHAIRMAN
    """
    # Проверяем уникальность имени
    existing = await repo.get_by_name(data.name)
    if existing:
        raise AlreadyExistsError(f"Подразделение с названием '{data.name}' уже существует")
    
    try:
        subdivision = await repo.create(data)
        logger.info(f"User {current_user.id} created subdivision {subdivision.id}")
        return subdivision
    except Exception as e:
        logger.error(f"Error creating subdivision: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании подразделения"
        )


@router.put("/{subdivision_id}", response_model=Subdivision)
async def update_subdivision(
    subdivision_id: int,
    data: SubdivisionUpdate,
    _: CSRFProtection,
    repo: SubdivisionRepo,
    current_user: CurrentUser = require_roles(["CHAIRMAN"])
):
    """
    Обновить подразделение.
    
    Требуется роль: CHAIRMAN
    """
    # Проверяем существование
    existing = await repo.get_by_id(subdivision_id)
    if not existing:
        raise NotFoundError(f"Подразделение с ID {subdivision_id} не найдено")
    
    # Проверяем уникальность нового имени
    if data.name and data.name != existing.name:
        duplicate = await repo.get_by_name(data.name)
        if duplicate:
            raise AlreadyExistsError(f"Подразделение с названием '{data.name}' уже существует")
    
    try:
        subdivision = await repo.update(subdivision_id, data)
        logger.info(f"User {current_user.id} updated subdivision {subdivision_id}")
        return subdivision
    except Exception as e:
        logger.error(f"Error updating subdivision: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении подразделения"
        )


@router.delete("/{subdivision_id}", response_model=SuccessResponse)
async def delete_subdivision(
    subdivision_id: int,
    _: CSRFProtection,
    repo: SubdivisionRepo,
    current_user: CurrentUser = require_roles(["CHAIRMAN"])
):
    """
    Удалить подразделение.
    
    Требуется роль: CHAIRMAN
    
    ВНИМАНИЕ: Удаление подразделения приведет к каскадному удалению всех связанных данных!
    """
    # Проверяем существование
    existing = await repo.get_by_id(subdivision_id)
    if not existing:
        raise NotFoundError(f"Подразделение с ID {subdivision_id} не найдено")
    
    # Проверяем наличие связанных данных
    stats = await repo.get_with_stats(subdivision_id)
    if stats.groups_count > 0 or stats.students_count > 0 or stats.users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить подразделение. Связанные данные: "
                   f"группы: {stats.groups_count}, студенты: {stats.students_count}, "
                   f"пользователи: {stats.users_count}"
        )
    
    try:
        success = await repo.delete(subdivision_id)
        if success:
            logger.info(f"User {current_user.id} deleted subdivision {subdivision_id}")
            return SuccessResponse(message="Подразделение успешно удалено")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении подразделения"
            )
    except Exception as e:
        logger.error(f"Error deleting subdivision: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении подразделения"
        )