from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Base schemas
class RoleBase(BaseModel):
    name: str

class SubdivisionBase(BaseModel):
    name: str

class AdditionalStatusBase(BaseModel):
    name: str

class GroupBase(BaseModel):
    name: str
    year: int = Field(default=2024, ge=2000, le=2100)
    subdivision_id: int

class UserBase(BaseModel):
    username: str
    subdivision_id: Optional[int] = None

class StudentDataBase(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None

class StudentBase(BaseModel):
    full_name: str
    group_id: int
    is_active: bool = False
    is_budget: bool
    year: int = Field(default=2024, ge=2000, le=2100)

class HostelStudentBase(BaseModel):
    hostel: int = Field(ge=1, le=20)
    room: int = Field(ge=1, le=9999)
    comment: Optional[str] = None

class ContributionBase(BaseModel):
    student_id: int
    semester: int = Field(ge=1, le=2)
    amount: Decimal = Field(ge=Decimal('0'), lt=Decimal('100000'))
    payment_date: Optional[date] = None
    year: int = Field(default=2024, ge=2000, le=2100)

# Create schemas
class RoleCreate(RoleBase):
    pass

class SubdivisionCreate(SubdivisionBase):
    pass

class AdditionalStatusCreate(AdditionalStatusBase):
    pass

class GroupCreate(GroupBase):
    pass

class UserCreate(UserBase):
    password: str

class StudentDataCreate(StudentDataBase):
    pass

class StudentCreate(StudentBase):
    data: Optional[StudentDataCreate] = None

class HostelStudentCreate(HostelStudentBase):
    student_id: int

class ContributionCreate(ContributionBase):
    pass

# Update schemas
class RoleUpdate(RoleBase):
    pass

class SubdivisionUpdate(SubdivisionBase):
    pass

class AdditionalStatusUpdate(AdditionalStatusBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = Field(None, ge=2000, le=2100)
    subdivision_id: Optional[int] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    subdivision_id: Optional[int] = None

class StudentDataUpdate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    group_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_budget: Optional[bool] = None
    year: Optional[int] = Field(None, ge=2000, le=2100)
    data: Optional[StudentDataUpdate] = None

class HostelStudentUpdate(BaseModel):
    hostel: Optional[int] = Field(None, ge=1, le=20)
    room: Optional[int] = Field(None, ge=1, le=9999)
    comment: Optional[str] = None

class ContributionUpdate(BaseModel):
    semester: Optional[int] = Field(None, ge=1, le=2)
    amount: Optional[Decimal] = Field(None, ge=Decimal('0'), lt=Decimal('100000'))
    payment_date: Optional[date] = None
    year: Optional[int] = Field(None, ge=2000, le=2100)

# Response schemas
class Role(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Subdivision(SubdivisionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AdditionalStatus(AdditionalStatusBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Group(GroupBase):
    id: int
    subdivision: Subdivision
    model_config = ConfigDict(from_attributes=True)

class StudentData(StudentDataBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class HostelStudent(HostelStudentBase):
    id: int
    student_id: int
    model_config = ConfigDict(from_attributes=True)

class Student(StudentBase):
    id: int
    data: Optional[StudentData]
    hostel: Optional[HostelStudent]
    additional_statuses: List[AdditionalStatus]
    group: Group
    model_config = ConfigDict(from_attributes=True)

class User(UserBase):
    id: int
    roles: List[Role]
    subdivision: Optional[Subdivision]
    model_config = ConfigDict(from_attributes=True)

class Contribution(ContributionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Статистика
class DivisionStats(BaseModel):
    division_id: int
    division_name: str
    students_count: int
    active_students_count: int
    groups_count: int

class GroupStats(BaseModel):
    group_id: int
    group_name: str
    students_count: int
    active_students_count: int
    division_name: str

class ContributionStats(BaseModel):
    year: int
    semester: int
    total_amount: Decimal
    paid_count: int
    unpaid_count: int
    total_students: int

class HostelStats(BaseModel):
    hostel_number: int
    total_rooms: int
    occupied_rooms: int
    total_students: int
    free_places: int

# Отчеты
class StudentReport(BaseModel):
    id: int
    full_name: str
    group_name: str
    division_name: str
    is_active: bool
    contribution_status: str
    hostel_info: Optional[str] = None
    additional_statuses: List[str] = []

class GroupReport(BaseModel):
    id: int
    name: str
    division_name: str
    students_count: int
    active_students_count: int
    contribution_stats: ContributionStats

class DivisionReport(BaseModel):
    id: int
    name: str
    groups_count: int
    students_count: int
    active_students_count: int
    contribution_stats: ContributionStats

# Дашборд
class DashboardStats(BaseModel):
    total_students: int
    active_students: int
    total_groups: int
    total_divisions: int
    hostel_occupancy: float
    contribution_collection_rate: float
    recent_activities: List[Dict[str, Any]]

# Экспорт
class ExportRequest(BaseModel):
    format: str = "xlsx"
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[Dict[str, str]] = None

class ExportResponse(BaseModel):
    file_url: str
    expires_at: date 