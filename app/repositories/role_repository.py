from typing import Optional, List
from asyncpg import Connection
from .base import BaseRepository
from ..models.role import Role, RoleCreate, RoleUpdate


class RoleRepository(BaseRepository[Role]):
    """Репозиторий для работы с ролями"""
    
    @property
    def table_name(self) -> str:
        return "roles"
    
    @property
    def model_class(self):
        return Role
    
    async def create(self, data: RoleCreate, conn: Optional[Connection] = None) -> Role:
        """Создать роль"""
        query = """
            INSERT INTO roles (name) 
            VALUES ($1) 
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, data.name)
            return Role(**dict(row))
    
    async def update(self, id: int, data: RoleUpdate, conn: Optional[Connection] = None) -> Optional[Role]:
        """Обновить роль"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(id, conn)
        
        query = """
            UPDATE roles 
            SET name = $2
            WHERE id = $1
            RETURNING *
        """
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, id, data.name)
            return Role(**dict(row)) if row else None
    
    async def get_by_name(self, name: str, conn: Optional[Connection] = None) -> Optional[Role]:
        """Получить роль по имени"""
        query = "SELECT * FROM roles WHERE name = $1"
        
        async with self._get_connection(conn) as connection:
            row = await connection.fetchrow(query, name)
            return Role(**dict(row)) if row else None
    
    async def get_by_user_id(self, user_id: int, conn: Optional[Connection] = None) -> List[Role]:
        """Получить роли пользователя"""
        query = """
            SELECT r.* FROM roles r
            JOIN userroles ur ON ur.roleid = r.id
            WHERE ur.userid = $1
        """
        
        async with self._get_connection(conn) as connection:
            rows = await connection.fetch(query, user_id)
            return [Role(**dict(row)) for row in rows]
