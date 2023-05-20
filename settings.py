"""File with settings and configs for the project"""
from envparse import Env

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    # connect string for the real database
    # драйвер подключения - asyncpg. Обязательно указать для асинхронного
    # подключения к базе.
    default="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres",
)

TEST_DATABASE_URL = env.str(
    # connect string for the test database
    "TEST_DATABASE_URL",
    default="postgresql+asyncpg://postgres_test:postgres_test@127.0.0.1:5433/postgres_test",
)
