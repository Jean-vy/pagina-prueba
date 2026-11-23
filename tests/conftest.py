import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app(str(tmp_path / "test.db"), str(tmp_path / "uploads"))


@pytest.fixture
def client(app):
    return app.test_client()
