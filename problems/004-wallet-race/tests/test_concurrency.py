import sys, os, tempfile, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app, Base, Wallet, get_db

_fd, _db_path = tempfile.mkstemp(suffix=".db")
TEST_ENGINE = create_engine(f"sqlite:///{_db_path}", connect_args={"check_same_thread": False})
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
    db.add_all([Wallet(id=1, owner="alice", balance=100), Wallet(id=2, owner="bob", balance=0), Wallet(id=3, owner="carol", balance=0)])
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
    resp = TestClient(app).post("/transfer", json={"from_wallet_id": 1, "to_wallet_id": 2, "amount": 60})
    assert resp.status_code == 200
    assert resp.json()["new_balance"] == 40

def test_insufficient_balance_rejected():
    _seed_db()
    resp = TestClient(app).post("/transfer", json={"from_wallet_id": 1, "to_wallet_id": 2, "amount": 999})
    assert resp.status_code == 400
    assert "Insufficient" in resp.json()["detail"]

def test_concurrent_transfers_no_overspend():
    _seed_db()
    results = []
    def do_transfer(amount, to_id):
        c = TestClient(app)
        resp = c.post("/transfer", json={"from_wallet_id": 1, "to_wallet_id": to_id, "amount": amount})
        results.append(resp.status_code)
    threads = [threading.Thread(target=do_transfer, args=(60, 2)), threading.Thread(target=do_transfer, args=(60, 3))]
    for t in threads: t.start()
    for t in threads: t.join()
    successes = [r for r in results if r == 200]
    assert len(successes) <= 1, f"Expected <=1 success, got {len(successes)}"
