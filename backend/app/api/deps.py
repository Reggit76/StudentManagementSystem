# backend/app/api/deps.py

from typing import Optional, Annotated, List
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from asyncpg import Pool
from loguru import logger

from ..core.database import db
from ..core.security import decode_token, verify_csrf_token
from ..core.exceptions import AuthenticationError, AuthorizationError, CSRFError
from ..models.auth import TokenData
from ..models.user import User
from ..models.common import QueryParams
from ..repositories.subdivision_repository import SubdivisionRepository
from ..repositories.role_repository import RoleRepository
from ..repositories.additional_status_repository import AdditionalStatusRepository
from ..repositories.group_repository import GroupRepository
from ..repositories.user_repository import UserRepository
from ..repositories.student_repository import StudentRepository
from ..repositories.hostel_repository import HostelRepository
from ..repositories.contribution_repository import ContributionRepository


# Security схема для JWT
security = HTTPBearer()


async def get_db_pool() -> Pool:
    """Получить пул соединений с БД"""
    if not db.pool:
        await db.connect()
    return db.pool


# Репозитории
async def get_subdivision_repository(
    pool: Pool = Depends(get_db_pool)
) -> SubdivisionRepository:
    """Получить репозиторий подразделений"""
    return SubdivisionRepository(pool)


async def get_role_repository(
    pool: Pool = Depends(get_db_pool)
) -> RoleRepository:
    """Получить репозиторий ролей"""
    return RoleRepository(pool)


async def get_additional_status_repository(
    pool: Pool = Depends(get_db_pool)
) -> AdditionalStatusRepository:
    """Получить репозиторий дополнительных статусов"""
    return AdditionalStatusRepository(pool)


async def get_group_repository(
    pool: Pool = Depends(get_db_pool)
) -> GroupRepository:
    """Получить репозиторий групп"""
    return GroupRepository(pool)


async def get_user_repository(
    pool: Pool = Depends(get_db_pool)
) -> UserRepository:
    """Получить репозиторий пользователей"""
    return UserRepository(pool)


async def get_student_repository(
    pool: Pool = Depends(get_db_pool)
) -> StudentRepository:
    """Получить репозиторий студентов"""
    return StudentRepository(pool)


async def get_hostel_repository(
    pool: Pool = Depends(get_db_pool)
) -> HostelRepository:
    """Получить репозиторий общежитий"""
    return HostelRepository(pool)


async def get_contribution_repository(
    pool: Pool = Depends(get_db_pool)
) -> ContributionRepository:
    """Получить репозиторий взносов"""
    return ContributionRepository(pool)


# Аутентификация
async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Получить данные из токена"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        raise AuthenticationError("Недействительный токен")
    
    return TokenData(
        user_id=payload.get("user_id"),
        login=payload.get("login"),
        roles=payload.get("roles", []),
        subdivision_id=payload.get("subdivision_id")
    )


async def get_current_user(
    token_data: TokenData = Depends(get_current_token),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """Получить текущего пользователя"""
    if not token_data.user_id:
        raise AuthenticationError("Недействительный токен")
    
    user = await user_repo.get_with_roles(token_data.user_id)
    if not user:
        raise AuthenticationError("Пользователь не найден")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Получить текущего активного пользователя"""
    # Здесь можно добавить проверку на активность пользователя
    return current_user


# CSRF защита для мутирующих операций
async def verify_csrf(
    request: Request,
    x_csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token")
):
    """Проверить CSRF токен"""
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        if not x_csrf_token:
            # В dev режиме можем пропустить CSRF проверку
            logger.warning("CSRF token not provided")
            return
        
        # Получаем CSRF токен из сессии
        session_csrf = getattr(request.state, "csrf_token", None)
        if not session_csrf:
            logger.warning("CSRF token not found in session")
            return
        
        if not verify_csrf_token(x_csrf_token, session_csrf):
            raise CSRFError("Недействительный CSRF токен")


# Проверка ролей
def require_roles(allowed_roles: List[str]):
    """Декоратор для проверки ролей пользователя"""
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        user_roles = [role.name for role in current_user.roles]
        
        # Проверяем, есть ли у пользователя хотя бы одна из разрешенных ролей
        if not any(role in allowed_roles for role in user_roles):
            raise AuthorizationError(
                f"Требуется одна из ролей: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


# Проверка принадлежности к подразделению
async def check_subdivision_access(
    subdivision_id: int,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Проверить доступ к подразделению"""
    user_roles = [role.name for role in current_user.roles]
    
    # Администраторы имеют доступ ко всем подразделениям
    if "Администратор" in user_roles:
        return current_user
    
    # Остальные пользователи имеют доступ только к своему подразделению
    if current_user.subdivisionid != subdivision_id:
        raise AuthorizationError("Нет доступа к данному подразделению")
    
    return current_user


# Пагинация
async def get_pagination_params(
    page: int = 1,
    size: int = 50,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> QueryParams:
    """Получить параметры пагинации"""
    if page < 1:
        raise ValueError("Номер страницы должен быть больше 0")
    
    if size < 1 or size > 100:
        raise ValueError("Размер страницы должен быть от 1 до 100")
    
    if sort_order not in ["asc", "desc"]:
        raise ValueError("Порядок сортировки должен быть 'asc' или 'desc'")
    
    return QueryParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )


# Типы для аннотаций
CurrentUser = Annotated[User, Depends(get_current_active_user)]
CurrentUserToken = Annotated[TokenData, Depends(get_current_token)]
PaginationParams = Annotated[QueryParams, Depends(get_pagination_params)]
CSRFProtection = Annotated[None, Depends(verify_csrf)]

# Репозитории с аннотациями
SubdivisionRepo = Annotated[SubdivisionRepository, Depends(get_subdivision_repository)]
RoleRepo = Annotated[RoleRepository, Depends(get_role_repository)]
AdditionalStatusRepo = Annotated[AdditionalStatusRepository, Depends(get_additional_status_repository)]
GroupRepo = Annotated[GroupRepository, Depends(get_group_repository)]
UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
StudentRepo = Annotated[StudentRepository, Depends(get_student_repository)]
HostelRepo = Annotated[HostelRepository, Depends(get_hostel_repository)]
ContributionRepo = Annotated[ContributionRepository, Depends(get_contribution_repository)]