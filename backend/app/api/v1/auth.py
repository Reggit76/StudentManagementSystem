from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from ...core.config import settings
from ...core.security import (
    verify_password, 
    create_access_token, 
    generate_csrf_token
)
from ...models.auth import Token, UserAuth
from ...models.user import User
from ...core.exceptions import AuthenticationError
from ..deps import UserRepo, get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepo = Depends()
) -> Any:
    """
    Авторизация пользователя.
    
    Возвращает access токен для доступа к API.
    """
    try:
        # Получаем пользователя
        user = await user_repo.get_by_login(form_data.username)
        if not user:
            raise AuthenticationError("Неверный логин или пароль")
        
        # Проверяем пароль
        if not verify_password(form_data.password, user.password_hash):
            raise AuthenticationError("Неверный логин или пароль")
        
        # Создаем токен
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        user_roles = [role.name for role in user.roles]
        
        token_data = {
            "user_id": user.id,
            "login": user.login,
            "roles": user_roles,
            "subdivision_id": user.subdivision_id
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        logger.info(f"User {user.login} logged in successfully")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при авторизации"
        )


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получить информацию о текущем пользователе.
    """
    return current_user


@router.post("/csrf-token")
async def get_csrf_token() -> dict:
    """
    Получить CSRF токен для защиты от CSRF атак.
    """
    csrf_token = generate_csrf_token()
    return {"csrf_token": csrf_token}


@router.post("/logout")
async def logout() -> dict:
    """
    Выход из системы.
    
    В текущей реализации с JWT токенами клиент просто удаляет токен.
    """
    return {"message": "Успешный выход из системы"}