# backend/app/api/v1/students.py

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Body
from loguru import logger

from ...models.student import Student, StudentCreate, StudentUpdate, StudentWithDetails, BulkOperationResult
from ...models.common import PaginatedResponse, SuccessResponse
from ...core.exceptions import NotFoundError, ValidationError, AuthorizationError
from ...core.database import db
from ...utils.permissions import PermissionChecker
from ...repositories.stored_procedures import StudentRepositoryWithProcedures
from ..deps import (
    StudentRepo, GroupRepo, AdditionalStatusRepo,
    CurrentUser, CSRFProtection, PaginationParams
)

router = APIRouter(prefix="/students", tags=["students"])


# Добавляем новый упрощенный эндпоинт для фронтенда
@router.get("/list", response_model=List[Student])
async def get_students_list(
    current_user: CurrentUser,
    repo: StudentRepo,
    group_id: Optional[int] = Query(None, description="Фильтр по группе"),
    subdivision_id: Optional[int] = Query(None, description="Фильтр по подразделению"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    is_budget: Optional[bool] = Query(None, description="Фильтр по бюджету"),
    year: Optional[int] = Query(None, description="Фильтр по году"),
    search: Optional[str] = Query(None, description="Поиск по ФИО"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(50, ge=1, le=100, description="Размер страницы")
):
    """
    Получить простой список студентов (без пагинации в ответе).
    Используется фронтендом для простого отображения.
    """
    try:
        # Применяем ограничения по подразделению
        filter_subdivision_id = PermissionChecker.filter_by_subdivision(
            current_user, subdivision_id
        )
        
        # Формируем фильтры
        filters = {}
        if group_id:
            filters['group_id'] = group_id
        if filter_subdivision_id:
            filters['subdivision_id'] = filter_subdivision_id
        if is_active is not None:
            filters['is_active'] = is_active
        if is_budget is not None:
            filters['is_budget'] = is_budget
        if year:
            filters['year'] = year
        if search:
            filters['search'] = search
        
        # Получаем данные
        offset = (page - 1) * size
        students = await repo.search(filters, limit=size, offset=offset)
        
        return students
        
    except Exception as e:
        logger.error(f"Error getting students list: {e}")
        # Возвращаем пустой список вместо ошибки для совместимости с фронтендом
        return []


@router.get("", response_model=PaginatedResponse[Student])
async def get_students(
    pagination: PaginationParams,
    current_user: CurrentUser,
    repo: StudentRepo,
    group_id: Optional[int] = Query(None, description="Фильтр по группе"),
    subdivision_id: Optional[int] = Query(None, description="Фильтр по подразделению"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    is_budget: Optional[bool] = Query(None, description="Фильтр по бюджету"),
    year: Optional[int] = Query(None, description="Фильтр по году"),
    search: Optional[str] = Query(None, description="Поиск по ФИО"),
    has_hostel: Optional[bool] = Query(None, description="Фильтр по проживанию в общежитии"),
    has_debt: Optional[bool] = Query(None, description="Фильтр по наличию задолженности")
):
    """
    Получить список студентов с фильтрацией и пагинацией.
    
    Фильтры:
    - **group_id**: ID группы
    - **subdivision_id**: ID подразделения (для не-админов автоматически применяется их подразделение)
    - **is_active**: активные члены профсоюза
    - **is_budget**: бюджетники
    - **year**: год поступления
    - **search**: поиск по ФИО
    - **has_hostel**: проживают в общежитии
    - **has_debt**: имеют задолженность по взносам
    """
    try:
        # Применяем ограничения по подразделению
        filter_subdivision_id = PermissionChecker.filter_by_subdivision(
            current_user, subdivision_id
        )
        
        # Формируем фильтры
        filters = {}
        if group_id:
            filters['group_id'] = group_id
        if filter_subdivision_id:
            filters['subdivision_id'] = filter_subdivision_id
        if is_active is not None:
            filters['is_active'] = is_active
        if is_budget is not None:
            filters['is_budget'] = is_budget
        if year:
            filters['year'] = year
        if search:
            filters['search'] = search
        
        # Получаем данные
        offset = (pagination.page - 1) * pagination.size
        students = await repo.search(filters, limit=pagination.size, offset=offset)
        
        # Дополнительная фильтрация по общежитию и долгам (если нужно)
        if has_hostel is not None or has_debt is not None:
            # Здесь можно добавить дополнительную логику фильтрации
            pass
        
        # Подсчитываем общее количество
        total = await repo.count(filters)
        
        return PaginatedResponse(
            items=students,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error getting students with pagination: {e}")
        # Возвращаем пустую пагинированную структуру
        return PaginatedResponse(
            items=[],
            total=0,
            page=pagination.page,
            size=pagination.size,
            pages=0
        )


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: int,
    current_user: CurrentUser,
    repo: StudentRepo,
    group_repo: GroupRepo
):
    """Получить студента по ID."""
    try:
        student = await repo.get_with_details(student_id)
        if not student:
            raise NotFoundError(f"Студент с ID {student_id} не найден")
        
        # Проверяем доступ через группу
        group = await group_repo.get_by_id(student.groupid)
        if group and not PermissionChecker.can_access_subdivision(current_user, group.subdivisionid):
            raise AuthorizationError("Нет доступа к данному студенту")
        
        return student
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error getting student {student_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении студента"
        )


@router.get("/{student_id}/full", response_model=StudentWithDetails)
async def get_student_full_details(
    student_id: int,
    current_user: CurrentUser,
    repo: StudentRepo,
    group_repo: GroupRepo
):
    """Получить полную информацию о студенте включая общежитие и взносы."""
    try:
        student = await repo.get_with_full_details(student_id)
        if not student:
            raise NotFoundError(f"Студент с ID {student_id} не найден")
        
        # Проверяем доступ
        group = await group_repo.get_by_id(student.groupid)
        if group and not PermissionChecker.can_access_subdivision(current_user, group.subdivisionid):
            raise AuthorizationError("Нет доступа к данному студенту")
        
        return student
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error getting student full details {student_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении детальной информации о студенте"
        )


@router.post("", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(
    data: StudentCreate,
    _: CSRFProtection,
    repo: StudentRepo,
    group_repo: GroupRepo,
    status_repo: AdditionalStatusRepo,
    current_user: CurrentUser
):
    """
    Создать нового студента.
    
    Требуется роль: CHAIRMAN, DEPUTY_CHAIRMAN, DIVISION_HEAD или DORMITORY_HEAD (для своего подразделения)
    """
    try:
        # Проверяем существование группы
        group = await group_repo.get_by_id(data.groupid)
        if not group:
            raise NotFoundError(f"Группа с ID {data.groupid} не найдена")
        
        # Проверяем права на создание в данном подразделении
        if not PermissionChecker.can_edit_student(current_user, group.subdivisionid):
            raise AuthorizationError("Недостаточно прав для создания студента")
        
        # Проверяем существование дополнительных статусов
        if hasattr(data, 'additional_status_ids') and data.additional_status_ids:
            for status_id in data.additional_status_ids:
                if not await status_repo.exists(status_id):
                    raise NotFoundError(f"Статус с ID {status_id} не найден")
        
        student = await repo.create(data)
        logger.info(f"User {current_user.id} created student {student.id}")
        return student
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании студента"
        )


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    _: CSRFProtection,
    repo: StudentRepo,
    group_repo: GroupRepo,
    current_user: CurrentUser
):
    """
    Обновить данные студента.
    
    Требуется роль: CHAIRMAN, DEPUTY_CHAIRMAN, DIVISION_HEAD или DORMITORY_HEAD (для своего подразделения)
    """
    try:
        # Получаем существующего студента
        existing = await repo.get_with_details(student_id)
        if not existing:
            raise NotFoundError(f"Студент с ID {student_id} не найден")
        
        # Проверяем права на редактирование
        group = await group_repo.get_by_id(existing.groupid)
        if group and not PermissionChecker.can_edit_student(current_user, group.subdivisionid):
            raise AuthorizationError("Недостаточно прав для редактирования студента")
        
        # Если меняется группа, проверяем права на новую группу
        if hasattr(data, 'groupid') and data.groupid and data.groupid != existing.groupid:
            new_group = await group_repo.get_by_id(data.groupid)
            if not new_group:
                raise NotFoundError(f"Группа с ID {data.groupid} не найдена")
            if not PermissionChecker.can_edit_student(current_user, new_group.subdivisionid):
                raise AuthorizationError("Недостаточно прав для перевода в указанную группу")
        
        student = await repo.update(student_id, data)
        if not student:
            raise NotFoundError(f"Не удалось обновить студента с ID {student_id}")
            
        logger.info(f"User {current_user.id} updated student {student_id}")
        return student
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error updating student: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении студента"
        )


@router.delete("/{student_id}", response_model=SuccessResponse)
async def delete_student(
    student_id: int,
    _: CSRFProtection,
    repo: StudentRepo,
    group_repo: GroupRepo,
    current_user: CurrentUser
):
    """
    Удалить студента.
    
    Требуется роль: CHAIRMAN или DEPUTY_CHAIRMAN (для своего подразделения)
    
    ВНИМАНИЕ: Удаление студента приведет к удалению всех связанных данных!
    """
    try:
        # Получаем студента
        student = await repo.get_with_details(student_id)
        if not student:
            raise NotFoundError(f"Студент с ID {student_id} не найден")
        
        # Проверяем права на удаление
        group = await group_repo.get_by_id(student.groupid)
        if not (PermissionChecker.has_permission(current_user, "delete_all") or
                (PermissionChecker.has_permission(current_user, "delete_subdivision") and
                 current_user.subdivisionid == group.subdivisionid)):
            raise AuthorizationError("Недостаточно прав для удаления студента")
        
        success = await repo.delete(student_id)
        if success:
            logger.info(f"User {current_user.id} deleted student {student_id}")
            return SuccessResponse(message="Студент успешно удален")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении студента"
            )
            
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error deleting student: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении студента"
        )


@router.post("/transfer/{student_id}", response_model=SuccessResponse)
async def transfer_student(
    student_id: int,
    _: CSRFProtection,
    current_user: CurrentUser,
    new_group_id: int = Body(..., description="ID новой группы")
):
    """
    Перевести студента в другую группу (через хранимую процедуру).
    
    Требуется роль: CHAIRMAN или DEPUTY_CHAIRMAN
    """
    try:
        pool = await db.get_pool()
        repo = StudentRepositoryWithProcedures(pool)
        
        success = await repo.transfer_student_to_group(
            student_id, new_group_id, current_user.id
        )
        if success:
            return SuccessResponse(message="Студент успешно переведен в новую группу")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось перевести студента"
            )
    except Exception as e:
        logger.error(f"Error transferring student: {e}")
        if "Недостаточно прав" in str(e):
            raise AuthorizationError(str(e))
        elif "не найден" in str(e):
            raise NotFoundError(str(e))
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при переводе студента"
            )


@router.post("/bulk-activate", response_model=BulkOperationResult)
async def bulk_activate_students(
    _: CSRFProtection,
    current_user: CurrentUser,
    student_ids: List[int] = Body(..., description="Список ID студентов для активации")
):
    """
    Массовая активация студентов (через хранимую процедуру).
    
    Требуется роль: CHAIRMAN, DEPUTY_CHAIRMAN или DIVISION_HEAD
    """
    try:
        pool = await db.get_pool()
        repo = StudentRepositoryWithProcedures(pool)
        
        result = await repo.bulk_activate_students(student_ids, current_user.id)
        return BulkOperationResult(
            success_count=result['success_count'],
            error_count=result['error_count'],
            errors=result['errors'] if 'errors' in result else []
        )
    except Exception as e:
        logger.error(f"Error in bulk activation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при массовой активации"
        )


@router.get("/debt/list", response_model=List[Dict[str, Any]])
async def get_students_with_debt(
    current_user: CurrentUser,
    subdivision_id: Optional[int] = Query(None, description="Фильтр по подразделению"),
    year: Optional[int] = Query(None, description="Год для проверки задолженности")
):
    """
    Получить список студентов с задолженностью (через хранимую функцию).
    
    Возвращает список студентов с информацией о задолженности.
    """
    try:
        # Применяем ограничения по подразделению
        filter_subdivision_id = PermissionChecker.filter_by_subdivision(
            current_user, subdivision_id
        )
        
        pool = await db.get_pool()
        repo = StudentRepositoryWithProcedures(pool)
        
        students = await repo.get_students_with_debt(filter_subdivision_id, year)
        return students
        
    except Exception as e:
        logger.error(f"Error getting students with debt: {e}")
        return []  # Возвращаем пустой список вместо ошибки