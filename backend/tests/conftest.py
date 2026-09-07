import pytest

from app.main import app


@pytest.fixture(autouse=True, scope="function")
async def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()
