import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./wallet.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, nullable=False)
    balance = Column(Integer, default=0)


class TransferLog(Base):
    __tablename__ = "transfer_logs"

    id = Column(Integer, primary_key=True, index=True)
    from_wallet_id = Column(Integer, nullable=False)
    to_wallet_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TransferRequest(BaseModel):
    from_wallet_id: int
    to_wallet_id: int
    amount: int


class WalletResponse(BaseModel):
    id: int
    owner: str
    balance: int


@app.get("/wallets/{wallet_id}", response_model=WalletResponse)
def get_wallet(wallet_id: int, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@app.post("/wallets", response_model=WalletResponse, status_code=201)
def create_wallet(owner: str, db: Session = Depends(get_db)):
    wallet = Wallet(owner=owner, balance=1000)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


@app.post("/transfer")
def transfer(req: TransferRequest, db: Session = Depends(get_db)):
    """Transfer money between wallets."""
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    if req.from_wallet_id == req.to_wallet_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to self")

    source = db.query(Wallet).filter(Wallet.id == req.from_wallet_id).first()
    target = db.query(Wallet).filter(Wallet.id == req.to_wallet_id).first()

    if not source or not target:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if source.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    source.balance -= req.amount
    target.balance += req.amount

    db.add(TransferLog(
        from_wallet_id=req.from_wallet_id,
        to_wallet_id=req.to_wallet_id,
        amount=req.amount,
    ))
    db.commit()

    return {"status": "ok", "new_balance": source.balance}
