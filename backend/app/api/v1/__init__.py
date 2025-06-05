# app/api/v1/__init__.py
from fastapi import APIRouter

from .auth import router as auth_router
from .subdivisions import router as subdivisions_router
from .roles import router as roles_router
from .additional_statuses import router as additional_statuses_router
from .groups import router as groups_router
from .students import router as students_router
from .contributions import router as contributions_router
from .hostels import router as hostels_router
from .users import router as users_router
from .audit_logs import router as audit_logs_router

# Создаем главный роутер для версии API v1
api_router = APIRouter(prefix="/api/v1")

# Подключаем все роутеры
api_router.include_router(auth_router)
api_router.include_router(subdivisions_router)
api_router.include_router(roles_router)
api_router.include_router(additional_statuses_router)
api_router.include_router(groups_router)
api_router.include_router(students_router)
api_router.include_router(contributions_router)
api_router.include_router(hostels_router)
api_router.include_router(users_router)
try:
    from .audit_logs import router as audit_logs_router
    api_router.include_router(audit_logs_router)
except ImportError as e:
    print(f"Warning: Could not import audit_logs router: {e}")

# Экспортируем для использования в main.py
__all__ = ["api_router"]