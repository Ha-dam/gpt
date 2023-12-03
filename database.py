from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

DATABASE_URL = "sqlite:///./test.db"  # 데이터 전송할 데이터베이스 URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    reply = Column(String, index=True)
    category = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

Base.metadata.create_all(bind=engine)

def create_diary_entry(db: Session, reply: str, category: str):
    db_entry = DiaryEntry(reply=reply, category=category)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry