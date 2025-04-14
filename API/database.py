# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, JSON, func, select, update, Boolean
from datetime import datetime, timezone
import uuid

DATABASE_URL = "sqlite+aiosqlite:///./plum_vision.db"

async_engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

class SessionMetrics(Base):
    __tablename__ = "session_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    is_active = Column(Boolean, default=True)
    total_images_processed = Column(Integer, default=0)
    predictions_by_category = Column(JSON, default={})
    predictions_by_class = Column(JSON, default={})
    start_time = Column(DateTime(timezone=True), default=func.now())
    last_updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=True)
    image_name = Column(String, index=True)
    predicted_class = Column(String)
    probability = Column(String)
    superclass = Column(String)
    inference_time = Column(String)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

async def get_active_session(db: AsyncSession) -> SessionMetrics | None:
    result = await db.execute(select(SessionMetrics).where(SessionMetrics.is_active == True))
    return result.scalar_one_or_none()

async def create_session_db(db: AsyncSession, session_id: str) -> SessionMetrics:
    print(f"Checking for existing active sessions to close before starting {session_id}")
    active_sessions_stmt = (
        update(SessionMetrics)
        .where(SessionMetrics.is_active == True)
        .values(
            is_active=False,
            end_time=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
    )
    await db.execute(active_sessions_stmt)
    await db.commit()

    existing_session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
    if existing_session.scalar_one_or_none():
        print(f"Reactivating existing session: {session_id}")
        stmt = (
            update(SessionMetrics)
            .where(SessionMetrics.session_id == session_id)
            .values(
                is_active=True,
                start_time=datetime.now(timezone.utc),
                end_time=None,
                duration_seconds=None,
                last_updated=datetime.now(timezone.utc)
            )
        )
        await db.execute(stmt)
        await db.commit()
        refreshed = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
        return refreshed.scalar_one()

    print(f"Creating new session in DB: {session_id}")
    new_session = SessionMetrics(session_id=session_id)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

async def update_session_stats_db(db: AsyncSession, session_id: str, superclass: str, predicted_class: str):
    session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
    session_obj = session.scalar_one_or_none()

    if not session_obj or not session_obj.is_active:
        print(f"Warning: Attempted to update inactive or non-existent session {session_id}")
        return None

    # Update superclass counts
    current_superclass_stats = session_obj.predictions_by_category if session_obj.predictions_by_category else {}
    current_superclass_stats[superclass] = current_superclass_stats.get(superclass, 0) + 1

    # Update class counts
    current_class_stats = session_obj.predictions_by_class if session_obj.predictions_by_class else {}
    current_class_stats[predicted_class] = current_class_stats.get(predicted_class, 0) + 1

    stmt = (
        update(SessionMetrics)
        .where(SessionMetrics.session_id == session_id)
        .values(
            total_images_processed=SessionMetrics.total_images_processed + 1,
            predictions_by_category=current_superclass_stats,
            predictions_by_class=current_class_stats,
            last_updated=datetime.now(timezone.utc)
        )
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()

    updated_session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
    return updated_session.scalar_one()


async def finalize_session_db(db: AsyncSession, session_id: str):
    print(f"Finalizing session in DB: {session_id}")
    session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
    session_obj = session.scalar_one_or_none()

    if not session_obj or not session_obj.is_active:
        print(f"Warning: Session {session_id} already finalized or doesn't exist.")
        return None

    end_time = datetime.now(timezone.utc)
    start_time = session_obj.start_time

    if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
        start_time = start_time.replace(tzinfo=timezone.utc)

    duration = int((end_time - start_time).total_seconds())

    stmt = (
        update(SessionMetrics)
        .where(SessionMetrics.session_id == session_id)
        .values(
            is_active=False,
            end_time=end_time,
            duration_seconds=duration,
            last_updated=end_time
        )
    )
    await db.execute(stmt)
    await db.commit()

    print(f"Session {session_id} finalized. Duration: {duration}s")
    finalized_session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
    return finalized_session.scalar_one()


async def add_prediction_db(db: AsyncSession, session_id: str, image_name: str, prediction_data: dict):
    top_prediction = prediction_data["prediction"][0]
    top_class_name = top_prediction["class"]
    top_probability = top_prediction["probability"]
    superclass = prediction_data["superclass_mapping"].get(top_class_name, "Unknown")
    inference_time = prediction_data["inference_time"]

    db_prediction = Prediction(
        session_id=session_id,
        image_name=image_name,
        predicted_class=top_class_name,
        probability=top_probability,
        superclass=superclass,
        inference_time=inference_time,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(db_prediction)

    # Remove this line - don't refresh before commit
    # await db.refresh(db_prediction)

    return db_prediction, superclass, top_class_name