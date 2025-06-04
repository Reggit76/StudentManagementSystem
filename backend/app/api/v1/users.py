# backend/app/api/v1/users.py

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from loguru import logger

from ...models.user import User, UserCreate, UserUpdate
from ...models.auth import ChangePasswordRequest
from ...models.common import PaginatedResponse, SuccessResponse
from ...core.exceptions import NotFoundError, AlreadyExistsError, AuthorizationError
from ...core.security import verify_password, get_password_hash
from ...utils.permissions import PermissionChecker
from ..deps import (
    UserRepo, RoleRepo, SubdivisionRepo,
    CurrentUser, CSRFProtection, PaginationParams,
    require_roles
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[User])
async def get_users(
    pagination: PaginationParams,
    current_user: CurrentUser,
    repo: UserRepo,
    subdivision_id: Optional[int] = Query(None, description="Фильтр по подразделению"),
    search: Optional[str] = Query(None, description="Поиск по логину")
):
    """
    Получить список пользователей.
    
    Администраторы видят всех пользователей.
    Остальные - только пользователей своего подразделения.
    """
    # Применяем ограничения по подразделению
    filter_subdivision_id = PermissionChecker.filter_by_subdivision(
        current_user, subdivision_id
    )
    
    # Получаем пользователей
    users = await repo.get_all_with_roles(filter_subdivision_id)
    
    # Фильтруем по поиску если нужно
    if search:
        users = [u for u in users if search.lower() in u.login.lower()]
    
    # Применяем пагинацию вручную
    offset = (pagination.page - 1) * pagination.size
    paginated_users = users[offset:offset + pagination.size]
    
    return PaginatedResponse(
        items=paginated_users,
        total=len(users),
        page=pagination.page,
        size=pagination.size,
        pages=(len(users) + pagination.size - 1) // pagination.size
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: CurrentUser):
    """Получить информацию о текущем пользователе."""
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: CurrentUser,
    repo: UserRepo
):
    """
    Получить пользователя по ID.
    
    Администраторы могут просматривать всех.
    Остальные - только себя и пользователей своего подразделения.
    """
    user = await repo.get_with_roles(user_id)
    if not user:
        raise NotFoundError(f"Пользователь с ID {user_id} не найден")
    
    # Проверяем права доступа
    if user_id != current_user.id:
        if not PermissionChecker.has_permission(current_user, "view_all"):
            if user.subdivisionid != current_user.subdivisionid:
                raise AuthorizationError("Нет доступа к данному пользователю")
    
    return user


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    _: CSRFProtection,
    repo: UserRepo,
    role_repo: RoleRepo,
    subdivision_repo: SubdivisionRepo,
    current_user: CurrentUser = require_roles(["Администратор"])
):
    """
    Создать нового пользователя.
    
    Требуется роль: Администратор
    """
    # Проверяем уникальность логина
    existing = await repo.get_by_login(data.login)
    if existing:
        raise AlreadyExistsError(f"Пользователь с логином '{data.login}' уже существует")
    
    # Проверяем существование подразделения
    if data.subdivisionid:
        subdivision = await subdivision_repo.get_by_id(data.subdivisionid)
        if not subdivision:
            raise NotFoundError(f"Подразделение с ID {data.subdivisionid} не найдено")
    
    # Проверяем существование ролей
    for role_id in data.role_ids:
        if not await role_repo.exists(role_id):
            raise NotFoundError(f"Роль с ID {role_id} не найдена")
    
    try:
        user = await repo.create(data)
        logger.info(f"User {current_user.id} created user {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании пользователя"
        )


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    data: UserUpdate,
    _: CSRFProtection,
    repo: UserRepo,
    role_repo: RoleRepo,
    subdivision_repo: SubdivisionRepo,
    current_user: CurrentUser
):
    """
    Обновить пользователя.
    
    Администраторы могут редактировать всех.
    Пользователи могут менять только свой пароль.
    """
    # Получаем существующего пользователя
    existing = await repo.get_with_roles(user_id)
    if not existing:
        raise NotFoundError(f"Пользователь с ID {user_id} не найден")
    
    # Проверяем права
    is_admin = PermissionChecker.has_permission(current_user, "manage_users")
    is_self = user_id == current_user.id
    
    if not is_admin and not is_self:
        raise AuthorizationError("Недостаточно прав для редактирования пользователя")
    
    # Если не админ, может менять только пароль
    if not is_admin:
        if data.subdivisionid is not None or data.role_ids is not None:
            raise AuthorizationError("Вы можете изменить только свой пароль")
    
    # Проверяем новое подразделение
    if data.subdivisionid and data.subdivisionid != existing.subdivisionid:
        subdivision = await subdivision_repo.get_by_id(data.subdivisionid)
        if not subdivision:
            raise NotFoundError(f"Подразделение с ID {data.subdivisionid} не найдено")
    
    # Проверяем новые роли
    if data.role_ids is not None:
        for role_id in data.role_ids:
            if not await role_repo.exists(role_id):
                raise NotFoundError(f"Роль с ID {role_id} не найдена")
    
    try:
        user = await repo.update(user_id, data)
        logger.info(f"User {current_user.id} updated user {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении пользователя"
        )


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    data: ChangePasswordRequest,
    _: CSRFProtection,
    repo: UserRepo,
    current_user: CurrentUser
):
    """Изменить свой пароль."""
    # Получаем пользователя с хешем пароля
    user_in_db = await repo.get_by_login(current_user.login)
    
    # Проверяем старый пароль
    if not verify_password(data.old_password, user_in_db.passwordhash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный старый пароль"
        )
    
    # Обновляем пароль
    update_data = UserUpdate(password=data.new_password)
    
    try:
        await repo.update(current_user.id, update_data)
        logger.info(f"User {current_user.id} changed password")
        return SuccessResponse(message="Пароль успешно изменен")
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при изменении пароля"
        )


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    _: CSRFProtection,
    repo: UserRepo,
    current_user: CurrentUser = require_roles(["Администратор"])
):
    """
    Удалить пользователя.
    
    Требуется роль: Администратор
    """
    # Проверяем существование
    existing = await repo.get_by_id(user_id)
    if not existing:
        raise NotFoundError(f"Пользователь с ID {user_id} не найден")
    
    # Нельзя удалить самого себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить самого себя"
        )
    
    try:
        success = await repo.delete(user_id)
        if success:
            logger.info(f"User {current_user.id} deleted user {user_id}")
            return SuccessResponse(message="Пользователь успешно удален")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении пользователя"
            )
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении пользователя"
        )


@router.post("/{user_id}/roles/{role_id}", response_model=SuccessResponse)
async def add_user_role(
    user_id: int,
    role_id: int,
    _: CSRFProtection,
    repo: UserRepo,
    role_repo: RoleRepo,
    current_user: CurrentUser = require_roles(["Администратор"])
):
    """
    Добавить роль пользователю.
    
    Требуется роль: Администратор
    """
    # Проверяем существование пользователя и роли
    if not await repo.exists(user_id):
        raise NotFoundError(f"Пользователь с ID {user_id} не найден")
    
    if not await role_repo.exists(role_id):
        raise NotFoundError(f"Роль с ID {role_id} не найдена")
    
    try:
        await repo.add_role(user_id, role_id)
        logger.info(f"User {current_user.id} added role {role_id} to user {user_id}")
        return SuccessResponse(message="Роль успешно добавлена")
    except Exception as e:
        logger.error(f"Error adding role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при добавлении роли"
        )


@router.delete("/{user_id}/roles/{role_id}", response_model=SuccessResponse)
async def remove_user_role(
    user_id: int,
    role_id: int,
    _: CSRFProtection,
    repo: UserRepo,
    current_user: CurrentUser = require_roles(["Администратор"])
):
    """
    Удалить роль у пользователя.
    
    Требуется роль: Администратор
    """
    try:
        success = await repo.remove_role(user_id, role_id)
        if success:
            logger.info(f"User {current_user.id} removed role {role_id} from user {user_id}")
            return SuccessResponse(message="Роль успешно удалена")
        else:
            return SuccessResponse(message="Роль не была назначена пользователю")
    except Exception as e:
        logger.error(f"Error removing role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении роли"
        )