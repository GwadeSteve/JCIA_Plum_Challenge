from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
import uuid

DATABASE_URL = "sqlite+aiosqlite:///./plum_vision.db"
# DATABASE_URL = "sqlite:///./plum_vision.db"      

async_engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

class SessionMetrics(Base):
    __tablename__ = "session_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    total_images_processed = Column(Integer, default=0)
    predictions_by_category = Column(JSON, default={})
    start_time = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_name = Column(String, index=True)
    predicted_class = Column(String)
    probability = Column(String)
    superclass = Column(String)
    inference_time = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db