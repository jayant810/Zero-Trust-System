from sqlalchemy import create_engine, Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database Path (relative to backend/)
DATABASE_URL = "sqlite:///./logs/zero_trust.db"

# Ensure logs directory exists
os.makedirs("./logs", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    jti = Column(String, primary_key=True, index=True)
    user_sub = Column(String, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    token_type = Column(String)  # 'access' or 'refresh'
    is_used = Column(Boolean, default=False)  # For refresh token reuse prevention

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
