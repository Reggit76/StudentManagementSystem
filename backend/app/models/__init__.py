# backend/app/models/__init__.py

from .auth import Token, TokenData, UserAuth, ChangePasswordRequest
from .user import User, UserCreate, UserUpdate, UserInDB
from .role import Role, RoleCreate, RoleUpdate
from .subdivision import Subdivision, SubdivisionCreate, SubdivisionUpdate, SubdivisionWithStats
from .group import Group, GroupCreate, GroupUpdate, GroupWithStats
from .student_data import StudentData, StudentDataCreate, StudentDataUpdate
from .student import Student, StudentCreate, StudentUpdate, StudentWithDetails, BulkOperationResult
from .additional_status import AdditionalStatus, AdditionalStatusCreate, AdditionalStatusUpdate
from .hostel_student import HostelStudent, HostelStudentCreate, HostelStudentUpdate
from .contribution import Contribution, ContributionCreate, ContributionUpdate, ContributionSummary
from .user_role import UserRole, UserRoleCreate, UserRoleUpdate
from .student_additional_status import StudentAdditionalStatus, StudentAdditionalStatusCreate, StudentAdditionalStatusUpdate
from .common import (
    QueryParams, PaginationParams, SortParams, FilterParams,
    PaginatedResponse, ErrorResponse, SuccessResponse, BulkOperationResult as CommonBulkOperationResult
)

__all__ = [
    # Auth
    "Token", "TokenData", "UserAuth", "ChangePasswordRequest",
    
    # User
    "User", "UserCreate", "UserUpdate", "UserInDB",
    
    # Role
    "Role", "RoleCreate", "RoleUpdate",
    
    # Subdivision
    "Subdivision", "SubdivisionCreate", "SubdivisionUpdate", "SubdivisionWithStats",
    
    # Group
    "Group", "GroupCreate", "GroupUpdate", "GroupWithStats",
    
    # Student Data
    "StudentData", "StudentDataCreate", "StudentDataUpdate",
    
    # Student
    "Student", "StudentCreate", "StudentUpdate", "StudentWithDetails", "BulkOperationResult",
    
    # Additional Status
    "AdditionalStatus", "AdditionalStatusCreate", "AdditionalStatusUpdate",
    
    # Hostel Student
    "HostelStudent", "HostelStudentCreate", "HostelStudentUpdate",
    
    # Contribution
    "Contribution", "ContributionCreate", "ContributionUpdate", "ContributionSummary",
    
    # Relations
    "UserRole", "UserRoleCreate", "UserRoleUpdate",
    "StudentAdditionalStatus", "StudentAdditionalStatusCreate", "StudentAdditionalStatusUpdate",
    
    # Common
    "QueryParams", "PaginationParams", "SortParams", "FilterParams",
    "PaginatedResponse", "ErrorResponse", "SuccessResponse", "CommonBulkOperationResult"
]