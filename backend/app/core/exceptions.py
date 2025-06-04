from typing import Optional, Dict, Any


class AppException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, code: Optional[str] = None, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    """Исключение для случаев, когда ресурс не найден"""
    def __init__(self, message: str = "Ресурс не найден", code: str = "NOT_FOUND"):
        super().__init__(message, code, 404)


class AlreadyExistsError(AppException):
    """Исключение для случаев, когда ресурс уже существует"""
    def __init__(self, message: str = "Ресурс уже существует", code: str = "ALREADY_EXISTS"):
        super().__init__(message, code, 409)


class ValidationError(AppException):
    """Исключение для ошибок валидации"""
    def __init__(self, message: str = "Ошибка валидации", code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, 422)
        self.details = details


class AuthenticationError(AppException):
    """Исключение для ошибок аутентификации"""
    def __init__(self, message: str = "Ошибка аутентификации", code: str = "AUTHENTICATION_ERROR"):
        super().__init__(message, code, 401)


class AuthorizationError(AppException):
    """Исключение для ошибок авторизации"""
    def __init__(self, message: str = "Недостаточно прав", code: str = "AUTHORIZATION_ERROR"):
        super().__init__(message, code, 403)


class CSRFError(AppException):
    """Исключение для CSRF ошибок"""
    def __init__(self, message: str = "Недействительный CSRF токен", code: str = "CSRF_ERROR"):
        super().__init__(message, code, 403)


class DatabaseError(AppException):
    """Исключение для ошибок БД"""
    def __init__(self, message: str = "Ошибка базы данных", code: str = "DATABASE_ERROR"):
        super().__init__(message, code, 500)


class BusinessLogicError(AppException):
    """Исключение для ошибок бизнес-логики"""
    def __init__(self, message: str, code: str = "BUSINESS_ERROR"):
        super().__init__(message, code, 400)
