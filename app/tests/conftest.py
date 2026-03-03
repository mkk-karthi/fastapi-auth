import os
import pytest
from sqlalchemy import text

os.environ["ENVIRONMENT"] = "test"

from app.core.database import Engine


def pytest_configure():
    import asyncio
    import inspect

    asyncio.iscoroutinefunction = inspect.iscoroutinefunction


TABLES = ["users"]


@pytest.fixture(scope="session", autouse=True)
def truncate_tables():
    with Engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

        for table in TABLES:
            conn.execute(text(f"TRUNCATE TABLE {table};"))

        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
