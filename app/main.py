from datetime import date, datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, String, Text, Date, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://habit_user:habit_password@localhost:5432/habit_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    habit_name: Mapped[str] = mapped_column(String(255), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LogCreate(BaseModel):
    habit_name: str
    log_date: date
    completed: bool = False
    notes: Optional[str] = None


class LogUpdate(BaseModel):
    habit_name: Optional[str] = None
    log_date: Optional[date] = None
    completed: Optional[bool] = None
    notes: Optional[str] = None


class LogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_name: str
    log_date: date
    completed: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


app = FastAPI(title="Habit Log API", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/logs", response_model=LogOut, status_code=201)
def create_log(payload: LogCreate, db: Session = Depends(get_db)) -> HabitLog:
    log = HabitLog(**payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@app.get("/logs", response_model=List[LogOut])
def list_logs(habit_name: Optional[str] = None, db: Session = Depends(get_db)) -> List[HabitLog]:
    query = db.query(HabitLog)
    if habit_name:
        query = query.filter(HabitLog.habit_name == habit_name)
    return query.order_by(HabitLog.log_date.desc()).all()


@app.get("/logs/{log_id}", response_model=LogOut)
def get_log(log_id: int, db: Session = Depends(get_db)) -> HabitLog:
    log = db.get(HabitLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@app.put("/logs/{log_id}", response_model=LogOut)
def update_log(log_id: int, payload: LogUpdate, db: Session = Depends(get_db)) -> HabitLog:
    log = db.get(HabitLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)
    return log


@app.delete("/logs/{log_id}", status_code=204)
def delete_log(log_id: int, db: Session = Depends(get_db)) -> None:
    log = db.get(HabitLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
