# backend/app/api/v1/hostels.py

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query
from loguru import logger

from ...models.hostel_student import (
    HostelStudent, HostelStudentCreate, HostelStudentUpdate
)
from ...models.common import PaginatedResponse, SuccessResponse
from ...core.exceptions import NotFoundError, ValidationError, AuthorizationError
from ...utils.permissions import PermissionChecker
from ..deps import (
    HostelRepo, StudentRepo, GroupRepo,
    CurrentUser, CSRFProtection, PaginationParams
)

router = APIRouter(prefix="/hostels", tags=["hostels"])


@router.get("", response_model=PaginatedResponse[HostelStudent])
async def get_hostel_students(
    pagination: PaginationParams,
    current_user: CurrentUser,
    repo: HostelRepo,
    hostel: Optional[int] = Query(None, ge=1, le=20, description="Номер общежития"),
    room: Optional[int] = Query(None, ge=1, description="Номер комнаты"),
    student_name: Optional[str] = Query(None, description="Поиск по ФИО студента")
):
    """
    Получить список проживающих в общежитии.
    
    Фильтры:
    - **hostel**: номер общежития (1-20)
    - **room**: номер комнаты
    - **student_name**: поиск по ФИО студента
    """
    # Формируем фильтры
    filters = {}
    if hostel:
        filters['hostel'] = hostel
    if room:
        filters['room'] = room
    if student_name:
        filters['student_name'] = student_name
    
    # Получаем данные
    offset = (pagination.page - 1) * pagination.size
    
    if filters:
        items = await repo.search(filters)
        # Применяем пагинацию вручную
        items = items[offset:offset + pagination.size]
    else:
        items = await repo.get_all(
            limit=pagination.size,
            offset=offset,
            order_by=pagination.sort_by or "hostel",
            order_desc=(pagination.sort_order == "desc")
        )
    
    # Подсчитываем общее количество
    total = await repo.count(filters if filters else None)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )


@router.get("/hostel/{hostel_number}", response_model=List[HostelStudent])
async def get_hostel_residents(
    hostel_number: int,
    current_user: CurrentUser,
    repo: HostelRepo
):
    """Получить всех проживающих в общежитии."""
    if hostel_number < 1 or hostel_number > 20:
        raise ValidationError("Номер общежития должен быть от 1 до 20")
    
    residents = await repo.get_by_hostel(hostel_number)
    return residents


@router.get("/room/{hostel_number}/{room_number}", response_model=List[HostelStudent])
async def get_room_residents(
    hostel_number: int,
    room_number: int,
    current_user: CurrentUser,
    repo: HostelRepo
):
    """Получить всех проживающих в комнате."""
    if hostel_number < 1 or hostel_number > 20:
        raise ValidationError("Номер общежития должен быть от 1 до 20")
    
    if room_number < 1:
        raise ValidationError("Номер комнаты должен быть положительным")
    
    residents = await repo.get_by_room(hostel_number, room_number)
    return residents


@router.get("/student/{student_id}", response_model=Optional[HostelStudent])
async def get_student_hostel(
    student_id: int,
    current_user: CurrentUser,
    repo: HostelRepo,
    student_repo: StudentRepo,
    group_repo: GroupRepo
):
    """Получить информацию о проживании студента в общежитии."""
    # Проверяем существование студента и доступ
    student = await student_repo.get_by_id(student_id)
    if not student:
        raise NotFoundError(f"Студент с ID {student_id} не найден")
    
    group = await group_repo.get_by_id(student.groupid)
    if not PermissionChecker.can_access_subdivision(current_user, group.subdivisionid):
        raise AuthorizationError("Нет доступа к данному студенту")
    
    hostel_info = await repo.get_by_student_id(student_id)
    return hostel_info


@router.post("", response_model=HostelStudent, status_code=status.HTTP_201_CREATED)
async def create_hostel_record(
    data: HostelStudentCreate,
    _: CSRFProtection,
    repo: HostelRepo,
    student_repo: StudentRepo,
    group_repo: GroupRepo,
    current_user: CurrentUser
):
    """
    Добавить запись о проживании студента в общежитии.
    
    Требуется роль: Администратор, Модератор или Оператор (для своего подразделения)
    """
    # Проверяем существование студента
    student = await student_repo.get_by_id(data.studentid)
    if not student:
        raise NotFoundError(f"Студент с ID {data.studentid} не найден")
    
    # Проверяем права
    group = await group_repo.get_by_id(student.groupid)
    if not PermissionChecker.can_edit_student(current_user, group.subdivisionid):
        raise AuthorizationError("Недостаточно прав для редактирования данных студента")
    
    # Проверяем, нет ли уже записи для этого студента
    existing = await repo.get_by_student_id(data.studentid)
    if existing:
        raise ValidationError(f"Студент уже проживает в общежитии {existing.hostel}, комната {existing.room}")
    
    try:
        hostel_record = await repo.create(data)
        logger.info(f"User {current_user.id} added hostel record for student {data.studentid}")
        return hostel_record
    except Exception as e:
        logger.error(f"Error creating hostel record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при добавлении записи об общежитии"
        )


@router.put("/{hostel_id}", response_model=HostelStudent)
async def update_hostel_record(
    hostel_id: int,
    data: HostelStudentUpdate,
    _: CSRFProtection,
    repo: HostelRepo,
    student_repo: StudentRepo,
    group_repo: GroupRepo,
    current_user: CurrentUser
):
    """
    Обновить запись о проживании в общежитии.
    
    Требуется роль: Администратор, Модератор или Оператор (для своего подразделения)
    """
    # Получаем существующую запись
    existing = await repo.get_with_student_name(hostel_id)
    if not existing:
        raise NotFoundError(f"Запись с ID {hostel_id} не найдена")
    
    # Проверяем права через студента
    student = await student_repo.get_by_id(existing.studentid)
    group = await group_repo.get_by_id(student.groupid)
    if not PermissionChecker.can_edit_student(current_user, group.subdivisionid):
        raise AuthorizationError("Недостаточно прав для редактирования данных студента")
    
    try:
        hostel_record = await repo.update(hostel_id, data)
        logger.info(f"User {current_user.id} updated hostel record {hostel_id}")
        return hostel_record
    except Exception as e:
        logger.error(f"Error updating hostel record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении записи об общежитии"
        )


@router.delete("/{hostel_id}", response_model=SuccessResponse)
async def delete_hostel_record(
    hostel_id: int,
    _: CSRFProtection,
    repo: HostelRepo,
    student_repo: StudentRepo,
    group_repo: GroupRepo,
    current_user: CurrentUser
):
    """
    Удалить запись о проживании в общежитии.
    
    Требуется роль: Администратор или Модератор (для своего подразделения)
    """
    # Получаем существующую запись
    existing = await repo.get_with_student_name(hostel_id)
    if not existing:
        raise NotFoundError(f"Запись с ID {hostel_id} не найдена")
    
    # Проверяем права через студента
    student = await student_repo.get_by_id(existing.studentid)
    group = await group_repo.get_by_id(student.groupid)
    if not (PermissionChecker.has_permission(current_user, "delete_all") or
            (PermissionChecker.has_permission(current_user, "delete_subdivision") and
             current_user.subdivisionid == group.subdivisionid)):
        raise AuthorizationError("Недостаточно прав для удаления записи")
    
    try:
        success = await repo.delete(hostel_id)
        if success:
            logger.info(f"User {current_user.id} deleted hostel record {hostel_id}")
            return SuccessResponse(message="Запись об общежитии успешно удалена")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении записи"
            )
    except Exception as e:
        logger.error(f"Error deleting hostel record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении записи"
        )