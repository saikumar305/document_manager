import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.postgres import get_db

from unittest.mock import MagicMock

# Test DB
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_client():
    return client


@pytest.fixture(scope="module")
def test_user():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }


@pytest.fixture(scope="module")
def auth_token(test_client, test_user):
    test_client.post("/auth/signup", json=test_user)
    response = test_client.post(
        "/auth/login",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    print(response.json())
    return response.json()["access_token"]


@pytest.fixture
def fake_vector_store():
    mock_store = MagicMock()
    mock_store.add = MagicMock()
    return mock_store


@pytest.fixture
def auth_header(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def mock_query_engine(monkeypatch):
 
    mock_response = MagicMock()
    mock_response.response = "This is a mocked answer."
    mock_node = MagicMock()
    mock_node.get_content.return_value = "Mocked source document."
    mock_node.metadata = {"page": 1, "title": "Test Upload"}
    mock_response.source_nodes = [mock_node]

    mock_engine = MagicMock()
    mock_engine.query.return_value = mock_response


    monkeypatch.setattr(
        "app.api.qa.RetrieverQueryEngine.from_args", lambda *args, **kwargs: mock_engine
    )
    return mock_engine
