from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import models, schemas
from app.repositories.base import BaseRepository
from app.api.auth import get_current_active_user

router = APIRouter(prefix="/divisions", tags=["divisions"])

def get_division_repository(db: Session = Depends(get_db)) -> BaseRepository:
    return BaseRepository(models.Subdivision, db)

@router.get("/", response_model=List[schemas.Subdivision])
async def read_divisions(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve divisions.
    """
    repo = get_division_repository(db)
    divisions = repo.get_multi(skip=skip, limit=limit)
    return divisions

@router.post("/", response_model=schemas.Subdivision)
async def create_division(
    *,
    division_in: schemas.SubdivisionCreate,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new division.
    """
    repo = get_division_repository(db)
    division = repo.create(division_in)
    return division

@router.get("/{id}", response_model=schemas.Subdivision)
async def read_division(
    id: int,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get division by ID.
    """
    repo = get_division_repository(db)
    division = repo.get(id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    return division

@router.put("/{id}", response_model=schemas.Subdivision)
async def update_division(
    *,
    id: int,
    division_in: schemas.SubdivisionUpdate,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update division.
    """
    repo = get_division_repository(db)
    division = repo.get(id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    division = repo.update(db_obj=division, obj_in=division_in)
    return division

@router.delete("/{id}", response_model=schemas.Subdivision)
async def delete_division(
    *,
    id: int,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete division.
    """
    repo = get_division_repository(db)
    division = repo.delete(id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    return division

@router.get("/{id}/groups", response_model=List[schemas.Group])
async def read_division_groups(
    *,
    id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get groups in a division.
    """
    repo = BaseRepository(models.Group, db)
    groups = repo.get_multi(
        skip=skip,
        limit=limit,
        filters={"SubdivisionID": id}
    )
    return groups

@router.get("/{id}/users", response_model=List[schemas.User])
async def read_division_users(
    *,
    id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get users in a division.
    """
    repo = BaseRepository(models.User, db)
    users = repo.get_multi(
        skip=skip,
        limit=limit,
        filters={"SubdivisionID": id}
    )
    return users 