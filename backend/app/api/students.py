from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.models.schemas import Student, StudentCreate, StudentUpdate, Contribution, HostelStudent
from app.repositories.student import StudentRepository
from app.services.auth import AuthService, get_auth_service
import asyncpg

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/", response_model=List[Student])
async def read_students(
    skip: int = 0,
    limit: int = 100,
    group_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    auth_service: AuthService = Depends(get_auth_service),
    conn: asyncpg.Connection = Depends(get_db)
) -> Any:
    """
    Retrieve students.
    """
    current_user = await auth_service.get_current_active_user()
    repo = StudentRepository(conn)
    
    filters = {}
    if group_id is not None:
        filters["GroupID"] = group_id
    if is_active is not None:
        filters["IsActive"] = is_active

    # Проверяем роль пользователя для фильтрации данных
    if "DIVISION_HEAD" in current_user.Roles:
        students = await repo.get_students_by_subdivision(current_user.SubdivisionID, limit, skip)
    else:
        students = await repo.get_all(limit=limit, offset=skip)
    
    return students

@router.post("/", response_model=Student)
async def create_student(
    student_in: StudentCreate,
    auth_service: AuthService = Depends(get_auth_service),
    conn: asyncpg.Connection = Depends(get_db)
) -> Any:
    """
    Create new student.
    """
    current_user = await auth_service.get_current_active_user()
    if "CHAIRMAN" not in current_user.Roles and "DEPUTY_CHAIRMAN" not in current_user.Roles:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    repo = StudentRepository(conn)
    student = await repo.create_student(student_in)
    return student

@router.get("/{id}", response_model=Student)
async def read_student(
    id: int,
    auth_service: AuthService = Depends(get_auth_service),
    conn: asyncpg.Connection = Depends(get_db)
) -> Any:
    """
    Get student by ID.
    """
    current_user = await auth_service.get_current_active_user()
    repo = StudentRepository(conn)
    student = await repo.get_student_with_details(id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Проверяем права доступа
    if "DIVISION_HEAD" in current_user.Roles:
        if student.Group.SubdivisionID != current_user.SubdivisionID:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return student

@router.put("/{id}", response_model=Student)
async def update_student(
    id: int,
    student_in: StudentUpdate,
    auth_service: AuthService = Depends(get_auth_service),
    conn: asyncpg.Connection = Depends(get_db)
) -> Any:
    """
    Update student.
    """
    current_user = await auth_service.get_current_active_user()
    repo = StudentRepository(conn)
    student = await repo.get_student_with_details(id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Проверяем права доступа
    if "CHAIRMAN" not in current_user.Roles and "DEPUTY_CHAIRMAN" not in current_user.Roles:
        if "DIVISION_HEAD" in current_user.Roles:
            if student.Group.SubdivisionID != current_user.SubdivisionID:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        else:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    student = await repo.update_student(id, student_in)
    return student

@router.delete("/{id}", response_model=Student)
async def delete_student(
    id: int,
    auth_service: AuthService = Depends(get_auth_service),
    conn: asyncpg.Connection = Depends(get_db)
) -> Any:
    """
    Delete student.
    """
    current_user = await auth_service.get_current_active_user()
    if "CHAIRMAN" not in current_user.Roles and "DEPUTY_CHAIRMAN" not in current_user.Roles:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    repo = StudentRepository(conn)
    student = await repo.get_by_id(id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    deleted = await repo.delete(id)
    if not deleted:
        raise HTTPException(status_code=400, detail="Could not delete student")
    
    return student

@router.get("/{id}/contributions", response_model=List[Contribution])
async def read_student_contributions(
    id: int,
    skip: int = 0,
    limit: int = 100,
    auth_service: AuthService = Depends(get_auth_service),
    conn: asyncpg.Connection = Depends(get_db)
) -> Any:
    """
    Get student's contributions.
    """
    current_user = await auth_service.get_current_active_user()
    repo = StudentRepository(conn)
    contributions = await repo.get_student_contributions(id, limit, skip)
    return contributions

@router.get("/{id}/hostel", response_model=Optional[HostelStudent])
async def read_student_hostel(
    id: int,
    auth_service: AuthService = Depends(get_auth_service),
    conn: asyncpg.Connection = Depends(get_db)
) -> Any:
    """
    Get student's hostel information.
    """
    current_user = await auth_service.get_current_active_user()
    repo = StudentRepository(conn)
    hostel = await repo.get_student_hostel(id)
    return hostel 