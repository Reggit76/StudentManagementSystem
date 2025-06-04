# backend/app/utils/permissions.py

from typing import List, Optional
from ..models.user import User
from ..core.exceptions import AuthorizationError


class PermissionChecker:
    """Класс для проверки прав доступа"""
    
    # Определение прав для ролей
    ROLE_PERMISSIONS = {
        "Администратор": [
            "view_all",
            "edit_all",
            "delete_all",
            "manage_users",
            "manage_roles",
            "manage_subdivisions",
            "manage_groups",
            "manage_students",
            "manage_contributions",
            "view_reports"
        ],
        "Модератор": [
            "view_subdivision",
            "edit_subdivision",
            "manage_groups_subdivision",
            "manage_students_subdivision",
            "manage_contributions_subdivision",
            "view_reports_subdivision"
        ],
        "Оператор": [
            "view_subdivision",
            "edit_students_subdivision",
            "edit_contributions_subdivision"
        ],
        "Наблюдатель": [
            "view_subdivision",
            "view_reports_subdivision"
        ]
    }
    
    @classmethod
    def has_permission(cls, user: User, permission: str) -> bool:
        """Проверить, есть ли у пользователя разрешение"""
        user_permissions = set()
        
        for role in user.roles:
            role_perms = cls.ROLE_PERMISSIONS.get(role.name, [])
            user_permissions.update(role_perms)
        
        return permission in user_permissions
    
    @classmethod
    def check_permission(cls, user: User, permission: str):
        """Проверить разрешение и выбросить исключение при отсутствии"""
        if not cls.has_permission(user, permission):
            raise AuthorizationError(f"Отсутствует разрешение: {permission}")
    
    @classmethod
    def can_access_subdivision(cls, user: User, subdivision_id: int) -> bool:
        """Проверить доступ к подразделению"""
        # Администраторы имеют доступ ко всем подразделениям
        if cls.has_permission(user, "view_all"):
            return True
        
        # Остальные - только к своему подразделению
        return user.subdivisionid == subdivision_id
    
    @classmethod
    def can_edit_student(cls, user: User, student_subdivision_id: int) -> bool:
        """Проверить возможность редактирования студента"""
        if cls.has_permission(user, "edit_all"):
            return True
        
        if cls.has_permission(user, "edit_students_subdivision"):
            return user.subdivisionid == student_subdivision_id
        
        return False
    
    @classmethod
    def can_manage_contributions(cls, user: User, subdivision_id: int) -> bool:
        """Проверить возможность управления взносами"""
        if cls.has_permission(user, "manage_contributions"):
            return True
        
        if cls.has_permission(user, "manage_contributions_subdivision"):
            return user.subdivisionid == subdivision_id
        
        return False
    
    @classmethod
    def filter_by_subdivision(cls, user: User, query_subdivision_id: Optional[int] = None) -> Optional[int]:
        """Получить ID подразделения для фильтрации"""
        # Администраторы могут видеть все или фильтровать по конкретному
        if cls.has_permission(user, "view_all"):
            return query_subdivision_id
        
        # Остальные видят только свое подразделение
        return user.subdivisionid