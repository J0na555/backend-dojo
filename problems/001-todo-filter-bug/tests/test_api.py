import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.main import app, Base, Todo, get_db

TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TEST_SESSION = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)

def override_get_db():
    db = TEST_SESSION()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def clean_db():
    db = TEST_SESSION()
    db.query(Todo).delete()
    db.commit()
    db.close()

def seed_todos():
    db = TEST_SESSION()
    db.add_all([Todo(title="buy milk", completed=False), Todo(title="pay bills", completed=True), Todo(title="call mom", completed=False), Todo(title="write report", completed=True)])
    db.commit()
    db.close()

def test_list_all():
    seed_todos()
    client = TestClient(app)
    resp = client.get("/todos")
    assert resp.status_code == 200
    assert len(resp.json()) == 4

def test_filter_completed_true():
    seed_todos()
    client = TestClient(app)
    resp = client.get("/todos?completed=true")
    assert resp.status_code == 200
    todos = resp.json()
    assert len(todos) == 2
    assert all(t["completed"] is True for t in todos)

def test_filter_completed_false():
    seed_todos()
    client = TestClient(app)
    resp = client.get("/todos?completed=false")
    assert resp.status_code == 200
    todos = resp.json()
    assert len(todos) == 2
    assert all(t["completed"] is False for t in todos)

def test_create_todo():
    client = TestClient(app)
    resp = client.post("/todos", json={"title": "test task"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "test task"
    assert data["completed"] is False
