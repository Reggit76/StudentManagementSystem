# ������������� ��
import asyncio
import asyncpg
from app.config import get_settings
from app.models.models import INIT_DATABASE_QUERIES
from app.services.auth import AuthService
from app.repositories.user import UserRepository

settings = get_settings()

async def init_db():
    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT
    )

    # Initialize database schema
    for query in INIT_DATABASE_QUERIES:
        await conn.execute(query)

    # Create superuser if it doesn't exist
    user_repo = UserRepository(conn)
    auth_service = AuthService(user_repo)

    existing_user = await user_repo.get_user_by_email(settings.FIRST_SUPERUSER_EMAIL)
    if not existing_user:
        password_hash = auth_service.get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
        await user_repo.create_user(
            username=settings.FIRST_SUPERUSER_USERNAME,
            email=settings.FIRST_SUPERUSER_EMAIL,
            password_hash=password_hash,
            role="admin"
        )
        print(f"Superuser {settings.FIRST_SUPERUSER_USERNAME} created successfully")
    else:
        print(f"Superuser {settings.FIRST_SUPERUSER_USERNAME} already exists")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(init_db())