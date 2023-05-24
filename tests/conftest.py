import asyncio
import subprocess
from datetime import timedelta
from typing import Any
from typing import Generator

import asyncpg
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

import settings
from db.session import get_db
from main import app
from security import create_access_token

CLEAN_TABLES = [
    "users",
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    # ChatGPT: Для закрытия loop в этой функции лучше использовать метод
    # asyncio.run() вместо loop.close().
    # asyncio.run() автоматически создает новый event loop, запускает
    # переданную ему корутину, и после завершения корутины автоматически
    # закрывает event loop.

    # Это исключает появление ошибки "RuntimeError: Event loop is closed"
    asyncio.run(loop.shutdown_asyncgens())


@pytest.fixture(scope="session", autouse=True)
async def run_migrations():
    working_directory = "."
    cmd_1 = ["alembic", "init", "migrations"]
    cmd_2 = ["alembic", "revision", "--autogenerate", "-m", "test"]
    cmd_3 = ["alembic", "upgrade", "heads"]

    for cmd in [cmd_1, cmd_2, cmd_3]:
        subprocess.Popen(
            cmd,
            shell=True,
            cwd=working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(f"""TRUNCATE TABLE {table_for_cleaning};""")


async def _get_test_db():
    try:
        # create async engine for interaction with database
        test_engine = create_async_engine(
            settings.TEST_DATABASE_URL, future=True, echo=True
        )

        # create session for the interaction with database
        test_async_session = sessionmaker(
            test_engine, expire_on_commit=False, class_=AsyncSession
        )

        yield test_async_session()

    finally:
        pass


@pytest.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the 'db_session'
    fiture to override the 'get_db' dependency that is injected
    into routes.
    """
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join(settings.TEST_DATABASE_URL.split("+asyncpg"))
    )
    yield pool
    await pool.close()


@pytest.fixture
async def get_user_from_database(asyncpg_pool):
    """Для тестов, которые будут нуждаться в функции чтения из базы данных
    по пользователю.
    """

    async def get_user_from_database_by_uuid(user_id: str):
        """Чтение данных из базы."""
        # Создание соединения с базой данных.
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch(
                """SELECT * FROM users WHERE user_id = $1;""", user_id
            )

    return get_user_from_database_by_uuid


@pytest.fixture
async def create_user_in_database(asyncpg_pool):
    async def create_user_in_database(
        user_id: str,
        name: str,
        surname: str,
        email: str,
        is_active: bool,
        hashed_password: str,
    ):
        async with asyncpg_pool.acquire() as connection:
            return await connection.execute(
                """INSERT INTO users VALUES ($1, $2, $3, $4, $5, $6)""",
                user_id,
                name,
                surname,
                email,
                is_active,
                hashed_password,
            )

    return create_user_in_database


def create_test_auth_headers_for_user(email: str) -> dict[str, str]:
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"Authorization": f"Bearer {access_token}"}
