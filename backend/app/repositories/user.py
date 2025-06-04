from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.schemas import User, UserCreate, UserUpdate
import asyncpg

class UserRepository(BaseRepository[User]):
    @property
    def table_name(self) -> str:
        return "Users"

    @property
    def model_class(self):
        return User

    async def create_user(
        self,
        user: UserCreate,
        conn: Optional[asyncpg.Connection] = None
    ) -> User:
        async with self._get_connection(conn) as connection:
            async with connection.transaction():
                # Создаем пользователя
                query = """
                    INSERT INTO Users (
                        Login, PasswordHash, SubdivisionID, IsActive
                    ) VALUES ($1, $2, $3, $4)
                    RETURNING *
                """
                values = (
                    user.Login,
                    user.PasswordHash,
                    user.SubdivisionID,
                    True
                )
                
                row = await connection.fetchrow(query, *values)
                user_id = row['id']
                
                # Добавляем роли
                if user.Roles:
                    roles_query = """
                        INSERT INTO UserRoles (UserID, RoleID)
                        SELECT $1, ID FROM Roles WHERE Name = ANY($2)
                    """
                    await connection.execute(roles_query, user_id, user.Roles)
                
                return User(**dict(row))

    async def update_user(
        self,
        id: int,
        user: UserUpdate,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[User]:
        async with self._get_connection(conn) as connection:
            async with connection.transaction():
                update_fields = []
                values = []
                param_count = 1

                for field, value in user.dict(exclude_unset=True).items():
                    if field != "Roles":
                        update_fields.append(f"{field} = ${param_count}")
                        values.append(value)
                        param_count += 1

                if update_fields:
                    values.append(id)
                    query = f"""
                        UPDATE Users 
                        SET {', '.join(update_fields)}
                        WHERE id = ${param_count}
                        RETURNING *
                    """
                    row = await connection.fetchrow(query, *values)
                else:
                    row = await connection.fetchrow(
                        "SELECT * FROM Users WHERE id = $1",
                        id
                    )

                if user.Roles is not None:
                    # Удаляем старые роли
                    await connection.execute(
                        "DELETE FROM UserRoles WHERE UserID = $1",
                        id
                    )
                    
                    # Добавляем новые роли
                    if user.Roles:
                        roles_query = """
                            INSERT INTO UserRoles (UserID, RoleID)
                            SELECT $1, ID FROM Roles WHERE Name = ANY($2)
                        """
                        await connection.execute(roles_query, id, user.Roles)

                return User(**dict(row)) if row else None

    async def get_user_with_roles(
        self,
        id: int,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[User]:
        query = """
            SELECT 
                u.*,
                array_agg(r.Name) as Roles,
                s.Name as SubdivisionName
            FROM Users u
            LEFT JOIN UserRoles ur ON u.ID = ur.UserID
            LEFT JOIN Roles r ON ur.RoleID = r.ID
            LEFT JOIN Subdivisions s ON u.SubdivisionID = s.ID
            WHERE u.ID = $1
            GROUP BY u.ID, s.ID
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id)
            return User(**dict(row)) if row else None

    async def get_user_by_login(
        self,
        login: str,
        conn: Optional[asyncpg.Connection] = None
    ) -> Optional[User]:
        query = """
            SELECT 
                u.*,
                array_agg(r.Name) as Roles
            FROM Users u
            LEFT JOIN UserRoles ur ON u.ID = ur.UserID
            LEFT JOIN Roles r ON ur.RoleID = r.ID
            WHERE u.Login = $1
            GROUP BY u.ID
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, login)
            return User(**dict(row)) if row else None

    async def check_user_role(
        self,
        user_id: int,
        role_name: str,
        conn: Optional[asyncpg.Connection] = None
    ) -> bool:
        query = """
            SELECT EXISTS (
                SELECT 1 FROM UserRoles ur
                JOIN Roles r ON ur.RoleID = r.ID
                WHERE ur.UserID = $1 AND r.Name = $2
            )
        """
        
        async with self._get_connection(conn) as connection:
            return await connection.fetchval(query, user_id, role_name)

    async def get_user(self, user_id: int) -> Optional[dict]:
        query = "SELECT * FROM users WHERE id = $1"
        record = await self.fetchrow(query, user_id)
        return dict(record) if record else None

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        query = "SELECT * FROM users WHERE username = $1"
        record = await self.fetchrow(query, username)
        return dict(record) if record else None

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        query = "SELECT * FROM users WHERE email = $1"
        record = await self.fetchrow(query, email)
        return dict(record) if record else None

    async def get_users_by_division(self, division_id: int) -> List[dict]:
        query = "SELECT * FROM users WHERE division_id = $1 ORDER BY username"
        records = await self.fetch(query, division_id)
        return [dict(record) for record in records]

    async def get_all_users(self) -> List[dict]:
        query = """
        SELECT u.*, d.name as division_name 
        FROM users u 
        LEFT JOIN divisions d ON u.division_id = d.id 
        ORDER BY u.username
        """
        records = await self.fetch(query)
        return [dict(record) for record in records]

    async def delete_user(self, user_id: int) -> bool:
        query = "DELETE FROM users WHERE id = $1"
        result = await self.execute(query, user_id)
        return "DELETE 1" in result

    async def change_password(self, user_id: int, new_password_hash: str) -> bool:
        query = "UPDATE users SET password_hash = $1 WHERE id = $2"
        result = await self.execute(query, new_password_hash, user_id)
        return "UPDATE 1" in result 