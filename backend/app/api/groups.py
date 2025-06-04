from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import models, schemas
from app.repositories.base import BaseRepository
from app.api.auth import get_current_active_user

router = APIRouter(prefix="/groups", tags=["groups"])

def get_group_repository(db: Session = Depends(get_db)) -> BaseRepository:
    return BaseRepository(models.Group, db)

@router.get("/", response_model=List[schemas.Group])
async def read_groups(
    skip: int = 0,
    limit: int = 100,
    subdivision_id: Optional[int] = None,
    year: Optional[int] = None,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve groups.
    """
    filters = {}
    if subdivision_id is not None:
        filters["SubdivisionID"] = subdivision_id
    if year is not None:
        filters["Year"] = year

    repo = get_group_repository(db)
    groups = repo.get_multi(skip=skip, limit=limit, filters=filters)
    return groups

@router.post("/", response_model=schemas.Group)
async def create_group(
    *,
    group_in: schemas.GroupCreate,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new group.
    """
    repo = get_group_repository(db)
    group = repo.create(group_in)
    return group

@router.get("/{id}", response_model=schemas.Group)
async def read_group(
    id: int,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get group by ID.
    """
    repo = get_group_repository(db)
    group = repo.get(id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/{id}", response_model=schemas.Group)
async def update_group(
    *,
    id: int,
    group_in: schemas.GroupUpdate,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update group.
    """
    repo = get_group_repository(db)
    group = repo.get(id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    group = repo.update(db_obj=group, obj_in=group_in)
    return group

@router.delete("/{id}", response_model=schemas.Group)
async def delete_group(
    *,
    id: int,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete group.
    """
    repo = get_group_repository(db)
    group = repo.delete(id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.get("/{id}/students", response_model=List[schemas.Student])
async def read_group_students(
    *,
    id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get students in a group.
    """
    repo = BaseRepository(models.Student, db)
    students = repo.get_multi(
        skip=skip,
        limit=limit,
        filters={"GroupID": id}
    )
    return students 