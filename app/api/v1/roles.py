from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from ...models.role import Role, RoleCreate, RoleUpdate
from ...models.common import SuccessResponse
from ...core.exceptions import NotFoundError, AlreadyExistsError
from ..deps import RoleRepo, CurrentUser, CSRFProtection, require_roles

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=List[Role])
async def get_roles(
    current_user: CurrentUser,
    repo: RoleRepo
):
    """Получить список всех ролей."""
    return await repo.get_all()


@router.get("/{role_id}", response_model=Role)
async def get_role(
    role_id: int,
    current_user: CurrentUser,
    repo: RoleRepo
):
    """Получить роль по ID."""
    role = await repo.get_by_id(role_id)
    if not role:
        raise NotFoundError(f"Роль с ID {role_id} не найдена")
    return role


@router.post("", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    _: CSRFProtection,
    repo: RoleRepo,
    current_user: CurrentUser = require_roles(["Администратор"])
):
    """
    Создать новую роль.
    
    Требуется роль: Администратор
    """
    # Проверяем уникальность имени
    existing = await repo.get_by_name(data.name)
    if existing:
        raise AlreadyExistsError(f"Роль с названием '{data.name}' уже существует")
    
    try:
        role = await repo.create(data)
        logger.info(f"User {current_user.id} created role {role.id}")
        return role
    except Exception as e:
        logger.error(f"Error creating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании роли"
        )


@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    _: CSRFProtection,
    repo: RoleRepo,
    current_user: CurrentUser = require_roles(["Администратор"])
):
    """
    Обновить роль.
    
    Требуется роль: Администратор
    """
    # Проверяем существование
    existing = await repo.get_by_id(role_id)
    if not existing:
        raise NotFoundError(f"Роль с ID {role_id} не найдена")
    
    # Защищаем системные роли
    system_roles = ["Администратор", "Модератор", "Оператор", "Наблюдатель"]
    if existing.name in system_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Системные роли нельзя изменять"
        )
    
    # Проверяем уникальность нового имени
    if data.name and data.name != existing.name:
        duplicate = await repo.get_by_name(data.name)
        if duplicate:
            raise AlreadyExistsError(f"Роль с названием '{data.name}' уже существует")
    
    try:
        role = await repo.update(role_id, data)
        logger.info(f"User {current_user.id} updated role {role_id}")
        return role
    except Exception as e:
        logger.error(f"Error updating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении роли"
        )


@router.delete("/{role_id}", response_model=SuccessResponse)
async def delete_role(
    role_id: int,
    _: CSRFProtection,
    repo: RoleRepo,
    current_user: CurrentUser = require_roles(["Администратор"])
):
    """
    Удалить роль.
    
    Требуется роль: Администратор
    """
    # Проверяем существование
    existing = await repo.get_by_id(role_id)
    if not existing:
        raise NotFoundError(f"Роль с ID {role_id} не найдена")
    
    # Защищаем системные роли
    system_roles = ["Администратор", "Модератор", "Оператор", "Наблюдатель"]
    if existing.name in system_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Системные роли нельзя удалять"
        )
    
    try:
        success = await repo.delete(role_id)
        if success:
            logger.info(f"User {current_user.id} deleted role {role_id}")
            return SuccessResponse(message="Роль успешно удалена")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении роли"
            )
    except Exception as e:
        logger.error(f"Error deleting role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении роли"
        )