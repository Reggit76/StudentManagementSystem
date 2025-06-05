# backend/app/api/v1/groups.py

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from loguru import logger

from ...models.group import Group, GroupCreate, GroupUpdate, GroupWithStats
from ...models.student import Student
from ...models.common import PaginatedResponse, SuccessResponse
from ...core.exceptions import NotFoundError, AlreadyExistsError, AuthorizationError
from ...utils.permissions import PermissionChecker
from ...services.audit_service import AuditService
from ..deps import (
    GroupRepo, SubdivisionRepo, StudentRepo, CurrentUser, CSRFProtection, 
    PaginationParams, require_roles
)

router = APIRouter(prefix="/groups", tags=["groups"])

@router.get("/list", response_model=List[Group])
async def get_groups_list(
    current_user: CurrentUser,
    repo: GroupRepo,
    subdivision_id: Optional[int] = Query(None, description="Фильтр по подразделению"),
    year: Optional[int] = Query(None, description="Фильтр по году"),
    search: Optional[str] = Query(None, description="Поиск по названию")
):
    """
    Получить простой список групп (без пагинации).
    Используется фронтендом для выпадающих списков и простого отображения.
    """
    try:
        # Применяем ограничения по подразделению
        filter_subdivision_id = PermissionChecker.filter_by_subdivision(
            current_user, subdivision_id
        )
        
        # Формируем фильтры
        filters = {}
        if filter_subdivision_id:
            filters['subdivision_id'] = filter_subdivision_id
        if year:
            filters['year'] = year
        if search:
            filters['search'] = search
        
        # Получаем группы
        if filters:
            items = await repo.search(filters, limit=1000, offset=0)
        else:
            items = await repo.get_all(limit=1000, offset=0, order_by="name")
        
        return items
        
    except Exception as e:
        logger.error(f"Error getting groups list: {e}")
        return []


@router.get("", response_model=PaginatedResponse[Group])
async def get_groups(
    pagination: PaginationParams,
    current_user: CurrentUser,
    repo: GroupRepo,
    subdivision_id: Optional[int] = Query(None, description="Фильтр по подразделению"),
    year: Optional[int] = Query(None, description="Фильтр по году"),
    search: Optional[str] = Query(None, description="Поиск по названию")
):
    """
    Получить список групп с пагинацией.
    
    - **subdivision_id**: фильтр по подразделению (для не-админов автоматически применяется их подразделение)
    - **year**: фильтр по году
    - **search**: поиск по названию
    """
    # Применяем ограничения по подразделению
    filter_subdivision_id = PermissionChecker.filter_by_subdivision(
        current_user, subdivision_id
    )
    
    # Формируем фильтры
    filters = {}
    if filter_subdivision_id:
        filters['subdivision_id'] = filter_subdivision_id
    if year:
        filters['year'] = year
    if search:
        filters['search'] = search
    
    # Подсчитываем общее количество
    total = await repo.count(filters)
    
    # Получаем данные
    offset = (pagination.page - 1) * pagination.size
    
    if filters:
        items = await repo.search(filters, limit=pagination.size, offset=offset)
    else:
        items = await repo.get_all(
            limit=pagination.size,
            offset=offset,
            order_by=pagination.sort_by or "name",
            order_desc=(pagination.sort_order == "desc")
        )
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


@router.get("/with-stats", response_model=List[GroupWithStats])
async def get_groups_with_stats(
    current_user: CurrentUser,
    repo: GroupRepo,
    year: Optional[int] = Query(None, description="Фильтр по году")
):
    """
    Получить все группы со статистикой.
    
    Возвращает список групп с количеством:
    - студентов
    - активных студентов
    - бюджетников
    """
    groups = await repo.get_all_with_stats(year)
    
    # Фильтруем по подразделению если не админ
    if not PermissionChecker.has_permission(current_user, "view_all"):
        groups = [g for g in groups if g.subdivisionid == current_user.subdivisionid]
    
    return groups


@router.get("/{group_id}", response_model=Group)
async def get_group(
    group_id: int,
    current_user: CurrentUser,
    repo: GroupRepo
):
    """Получить группу по ID."""
    group = await repo.get_by_id(group_id)
    if not group:
        raise NotFoundError(f"Группа с ID {group_id} не найдена")
    
    # Проверяем доступ
    if not PermissionChecker.can_access_subdivision(current_user, group.subdivisionid):
        raise AuthorizationError("Нет доступа к данной группе")
    
    return group


@router.get("/{group_id}/stats", response_model=GroupWithStats)
async def get_group_stats(
    group_id: int,
    current_user: CurrentUser,
    repo: GroupRepo
):
    """Получить группу со статистикой."""
    group = await repo.get_with_stats(group_id)
    if not group:
        raise NotFoundError(f"Группа с ID {group_id} не найдена")
    
    # Проверяем доступ
    if not PermissionChecker.can_access_subdivision(current_user, group.subdivisionid):
        raise AuthorizationError("Нет доступа к данной группе")
    
    return group


@router.get("/{group_id}/students", response_model=List[Student])
async def get_group_students(
    group_id: int,
    current_user: CurrentUser,
    repo: GroupRepo,
    student_repo: StudentRepo
):
    """Получить список студентов группы"""
    # Проверяем существование группы
    group = await repo.get_by_id(group_id)
    if not group:
        raise NotFoundError(f"Группа с ID {group_id} не найдена")
    
    # Проверяем доступ
    if not PermissionChecker.can_access_subdivision(current_user, group.subdivisionid):
        raise AuthorizationError("Нет доступа к данной группе")
    
    try:
        # Получаем студентов
        filters = {"group_id": group_id}
        students = await student_repo.search(filters, limit=1000)
        
        # Логируем просмотр
        await AuditService.log_action(
            user_id=current_user.id,
            action="VIEW",
            table_name="students",
            record_id=None,
            new_data={"group_id": group_id, "action": "view_group_students"}
        )
        
        return students
        
    except Exception as e:
        logger.error(f"Error getting group students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении студентов группы"
        )


@router.post("", response_model=Group, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    request: Request,
    _: CSRFProtection,
    repo: GroupRepo,
    subdivision_repo: SubdivisionRepo,
    current_user: CurrentUser
):
    """
    Создать новую группу.
    
    Требуется роль: Администратор или Модератор (для своего подразделения)
    """
    # Проверяем права на создание в указанном подразделении
    if not (PermissionChecker.has_permission(current_user, "manage_groups") or
            (PermissionChecker.has_permission(current_user, "manage_groups_subdivision") and
             current_user.subdivisionid == data.subdivisionid)):
        raise AuthorizationError("Недостаточно прав для создания группы")
    
    # Проверяем существование подразделения
    subdivision = await subdivision_repo.get_by_id(data.subdivisionid)
    if not subdivision:
        raise NotFoundError(f"Подразделение с ID {data.subdivisionid} не найдено")
    
    # Проверяем уникальность имени
    existing = await repo.get_by_name(data.name)
    if existing:
        raise AlreadyExistsError(f"Группа с названием '{data.name}' уже существует")
    
    try:
        group = await repo.create(data)
        
        # Логируем создание
        await AuditService.log_create(
            user_id=current_user.id,
            table_name="groups",
            record_id=group.id,
            data=group.model_dump(),
            request=request
        )
        
        logger.info(f"User {current_user.id} created group {group.id}")
        return group
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании группы"
        )


@router.put("/{group_id}", response_model=Group)
async def update_group(
    group_id: int,
    data: GroupUpdate,
    request: Request,
    _: CSRFProtection,
    repo: GroupRepo,
    current_user: CurrentUser
):
    """
    Обновить группу.
    
    Требуется роль: Администратор или Модератор (для своего подразделения)
    """
    # Получаем существующую группу
    existing = await repo.get_by_id(group_id)
    if not existing:
        raise NotFoundError(f"Группа с ID {group_id} не найдена")
    
    # Проверяем права на редактирование
    if not (PermissionChecker.has_permission(current_user, "edit_all") or
            (PermissionChecker.has_permission(current_user, "edit_subdivision") and
             current_user.subdivisionid == existing.subdivisionid)):
        raise AuthorizationError("Недостаточно прав для редактирования группы")
    
    # Проверяем уникальность нового имени
    if data.name and data.name != existing.name:
        duplicate = await repo.get_by_name(data.name)
        if duplicate:
            raise AlreadyExistsError(f"Группа с названием '{data.name}' уже существует")
    
    try:
        # Сохраняем старые данные для лога
        old_data = existing.model_dump()
        
        group = await repo.update(group_id, data)
        
        # Логируем обновление
        await AuditService.log_update(
            user_id=current_user.id,
            table_name="groups",
            record_id=group_id,
            old_data=old_data,
            new_data=group.model_dump(),
            request=request
        )
        
        logger.info(f"User {current_user.id} updated group {group_id}")
        return group
    except Exception as e:
        logger.error(f"Error updating group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении группы"
        )


@router.delete("/{group_id}", response_model=SuccessResponse)
async def delete_group(
    group_id: int,
    request: Request,
    _: CSRFProtection,
    repo: GroupRepo,
    current_user: CurrentUser
):
    """
    Удалить группу.
    
    Требуется роль: Администратор или Модератор (для своего подразделения)
    
    ВНИМАНИЕ: Удаление группы приведет к каскадному удалению всех студентов!
    """
    # Получаем группу
    group = await repo.get_with_stats(group_id)
    if not group:
        raise NotFoundError(f"Группа с ID {group_id} не найдена")
    
    # Проверяем права на удаление
    if not (PermissionChecker.has_permission(current_user, "delete_all") or
            (PermissionChecker.has_permission(current_user, "delete_subdivision") and
             current_user.subdivisionid == group.subdivisionid)):
        raise AuthorizationError("Недостаточно прав для удаления группы")
    
    # Проверяем наличие студентов
    if group.students_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить группу. В группе есть {group.students_count} студентов"
        )
    
    try:
        # Сохраняем данные для лога
        group_data = group.model_dump()
        
        success = await repo.delete(group_id)
        if success:
            # Логируем удаление
            await AuditService.log_delete(
                user_id=current_user.id,
                table_name="groups",
                record_id=group_id,
                data=group_data,
                request=request
            )
            
            logger.info(f"User {current_user.id} deleted group {group_id}")
            return SuccessResponse(message="Группа успешно удалена")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении группы"
            )
    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении группы"
        )