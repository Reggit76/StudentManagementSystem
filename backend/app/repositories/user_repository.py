# backend/app/repositories/user_repository.py

from typing import Optional, List
from asyncpg import Connection
from .base import BaseRepository
from ..models.user import User, UserCreate, UserUpdate, UserInDB
from ..models.role import Role
from ..core.security import get_password_hash


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями"""
    
    @property
    def table_name(self) -> str:
        return "users"
    
    @property
    def model_class(self):
        return User
    
    async def create(self, data: UserCreate, conn: Optional[Connection] = None) -> User:
        """Создать пользователя"""
        password_hash = get_password_hash(data.password)
        
        async with self._get_connection(conn) as connection:
            # Создаем пользователя
            user_query = """
                INSERT INTO users (login, passwordhash, subdivisionid) 
                VALUES ($1, $2, $3) 
                RETURNING *
            """
            user_row = await connection.fetchrow(
                user_query, 
                data.login, 
                password_hash, 
                data.subdivisionid
            )
            
            # Добавляем роли
            if data.role_ids:
                role_query = """
                    INSERT INTO userroles (userid, roleid) 
                    VALUES ($1, $2)
                """
                role_data = [(user_row['id'], role_id) for role_id in data.role_ids]
                await connection.executemany(role_query, role_data)
            
            # Получаем пользователя с ролями
            return await self.get_with_roles(user_row['id'], connection)
    
    async def update(self, id: int, data: UserUpdate, conn: Optional[Connection] = None) -> Optional[User]:
        """Обновить пользователя"""
        update_data = data.model_dump(exclude_unset=True, exclude={'role_ids'})
        
        async with self._get_connection(conn) as connection:
            # Обновляем данные пользователя
            if update_data:
                if 'password' in update_data:
                    update_data['passwordhash'] = get_password_hash(update_data.pop('password'))
                
                set_parts = []
                values = [id]
                for i, (field, value) in enumerate(update_data.items()):
                    set_parts.append(f"{field} = ${i+2}")
                    values.append(value)
                
                query = f"""
                    UPDATE users 
                    SET {', '.join(set_parts)}
                    WHERE id = $1
                    RETURNING *
                """
                await connection.fetchrow(query, *values)
            
            # Обновляем роли, если переданы
            if data.role_ids is not None:
                # Удаляем старые роли
                await connection.execute("DELETE FROM userroles WHERE userid = $1", id)
                
                # Добавляем новые роли
                if data.role_ids:
                    role_query = """
                        INSERT INTO userroles (userid, roleid) 
                        VALUES ($1, $2)
                    """
                    role_data = [(id, role_id) for role_id in data.role_ids]
                    await connection.executemany(role_query, role_data)
            
            return await self.get_with_roles(id, connection)
    
    async def get_by_login(self, login: str, conn: Optional[Connection] = None) -> Optional[UserInDB]:
        """Получить пользователя по логину с хешем пароля"""
        query = """
            SELECT u.*, s.name as subdivision_name
            FROM users u
            LEFT JOIN subdivisions s ON s.id = u.subdivisionid
            WHERE u.login = $1
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, login)
            if not row:
                return None
            
            # Получаем роли
            roles = await self._get_user_roles(row['id'], connection)
            
            user_data = dict(row)
            user_data['roles'] = roles
            
            return UserInDB(**user_data)
    
    async def get_with_roles(self, id: int, conn: Optional[Connection] = None) -> Optional[User]:
        """Получить пользователя с ролями"""
        query = """
            SELECT u.*, s.name as subdivision_name
            FROM users u
            LEFT JOIN subdivisions s ON s.id = u.subdivisionid
            WHERE u.id = $1
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            if not row:
                return None
            
            # Получаем роли
            roles = await self._get_user_roles(id, connection)
            
            user_data = dict(row)
            user_data['roles'] = roles
            # Убираем пароль из результата
            user_data.pop('passwordhash', None)
            
            return User(**user_data)
    
    async def get_all_with_roles(self, subdivision_id: Optional[int] = None, conn: Optional[Connection] = None) -> List[User]:
        """Получить всех пользователей с ролями"""
        base_query = """
            SELECT u.*, s.name as subdivision_name
            FROM users u
            LEFT JOIN subdivisions s ON s.id = u.subdivisionid
        """
        
        if subdivision_id:
            query = base_query + " WHERE u.subdivisionid = $1 ORDER BY u.login"
            params = [subdivision_id]
        else:
            query = base_query + " ORDER BY u.login"
            params = []
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, *params)
            users = []
            
            for row in rows:
                roles = await self._get_user_roles(row['id'], connection)
                user_data = dict(row)
                user_data['roles'] = roles
                user_data.pop('passwordhash', None)
                users.append(User(**user_data))
            
            return users
    
    async def _get_user_roles(self, user_id: int, conn: Connection) -> List[Role]:
        """Получить роли пользователя"""
        query = """
            SELECT r.* FROM roles r
            JOIN userroles ur ON ur.roleid = r.id
            WHERE ur.userid = $1
        """
        rows = await conn.fetch(query, user_id)
        return [Role(**dict(row)) for row in rows]
    
    async def add_role(self, user_id: int, role_id: int, conn: Optional[Connection] = None) -> bool:
        """Добавить роль пользователю"""
        query = """
            INSERT INTO userroles (userid, roleid) 
            VALUES ($1, $2)
            ON CONFLICT (userid, roleid) DO NOTHING
        """
        
        async with self._get_connection(conn) as connection:
            await connection.execute(query, user_id, role_id)
            return True
    
    async def remove_role(self, user_id: int, role_id: int, conn: Optional[Connection] = None) -> bool:
        """Удалить роль у пользователя"""
        query = "DELETE FROM userroles WHERE userid = $1 AND roleid = $2"
        
        async with self._get_connection(conn) as connection:
            result = await connection.execute(query, user_id, role_id)
            return result != "DELETE 0"