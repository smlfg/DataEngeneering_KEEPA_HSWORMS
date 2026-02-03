import pytest
import asyncio
from datetime import timedelta


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_relaxed_compare_transform(a, b):
    return a == b


pytest.relpath = lambda expected: pytest.approx(expected, rel=0.01)
