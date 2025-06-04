from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.repositories.user import UserRepository
from app.core.database import get_db
from app.models.schemas import TokenData, User, UserCreate
import asyncpg

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

ALGORITHM = "HS256"

class AuthService:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
        self.user_repo = UserRepository(conn)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_user_by_login(username)
        if not user:
            return None
        if not self.verify_password(password, user.PasswordHash):
            return None
        return user

    def create_access_token(
        self,
        user_id: int,
        roles: List[str],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = {"user_id": user_id, "roles": roles}
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("user_id")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = await self.user_repo.get_user_with_roles(user_id)
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.IsActive:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    def decode_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("user_id")
            roles: List[str] = payload.get("roles", [])
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token_data = TokenData(user_id=user_id, roles=roles)
            return token_data
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def create_user(self, user: UserCreate) -> User:
        # Проверяем, что пользователь с таким логином не существует
        existing_user = await self.user_repo.get_user_by_login(user.Login)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this login already exists"
            )
        
        # Хэшируем пароль
        user.PasswordHash = self.get_password_hash(user.Password)
        
        # Создаем пользователя
        return await self.user_repo.create_user(user)

async def get_auth_service(conn=Depends(get_db)) -> AuthService:
    return AuthService(conn) 