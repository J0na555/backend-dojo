import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import threading
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.main import app, Base, Wallet, get_db, SessionLocal

# Use a temp file for concurrent tests so each thread gets its own connection
# to the same database
_fd, _db_path = tempfile.mkstemp(suffix=".db")


def _make_test_engine():
    return create_engine(f"sqlite:///{_db_path}", connect_args={"check_same_thread": False})


TEST_ENGINE = _make_test_engine()
TEST_SESSION = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)


def override_get_db():
    db = TEST_SESSION()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def _seed_db():
    db = TEST_SESSION()
    db.query(Wallet).delete()
    db.add_all([
        Wallet(id=1, owner="alice", balance=100),
        Wallet(id=2, owner="bob", balance=0),
        Wallet(id=3, owner="carol", balance=0),
    ])
    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def setup_db():
    _seed_db()
    yield


def teardown_module(module):
    os.close(_fd)
    os.unlink(_db_path)


def test_single_transfer_ok():
    _seed_db()
    client = TestClient(app)
    resp = client.post("/transfer", json={
        "from_wallet_id": 1,
        "to_wallet_id": 2,
        "amount": 60,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_balance"] == 40


def test_insufficient_balance_rejected():
    _seed_db()
    client = TestClient(app)
    resp = client.post("/transfer", json={
        "from_wallet_id": 1,
        "to_wallet_id": 2,
        "amount": 999,
    })
    assert resp.status_code == 400
    assert "Insufficient" in resp.json()["detail"]


def test_concurrent_transfers_no_overspend():
    # The balance check and update aren't atomic, but a single racing pair
    # only *sometimes* trips the race. Run it many times and assert the
    # money-conservation invariant holds on EVERY attempt: a correct fix is
    # green on every run, the race corrupts the invariant with overwhelming
    # probability across the loop.
    iterations = 50

    def do_transfer(to_id):
        c = TestClient(app)
        return c.post("/transfer", json={
            "from_wallet_id": 1,
            "to_wallet_id": to_id,
            "amount": 60,
        }).status_code

    for attempt in range(iterations):
        _seed_db()
        results = []
        threads = [
            threading.Thread(target=lambda: results.append(do_transfer(2))),
            threading.Thread(target=lambda: results.append(do_transfer(3))),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        successes = sum(1 for r in results if r == 200)
        assert successes <= 1, (
            f"attempt {attempt + 1}: {successes} transfers of 60 succeeded "
            "from a balance of 100 — overspend (lost update)."
        )

        db = TEST_SESSION()
        total = sum(w.balance for w in db.query(Wallet).all())
        db.close()
        assert total == 100, (
            f"attempt {attempt + 1}: money not conserved, total balance "
            f"{total} != 100"
        )
