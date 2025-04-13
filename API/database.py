from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, JSON, func, select, update, Boolean
from datetime import datetime, timezone
import uuid

DATABASE_URL = "sqlite+aiosqlite:///./plum_vision.db"

# Create async engine and session factory
async_engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Define the database tables using SQLAlchemy ORM models
class SessionMetrics(Base):
    __tablename__ = "session_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    is_active = Column(Boolean, default=True)
    total_images_processed = Column(Integer, default=0)
    predictions_by_category = Column(JSON, default={})
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
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

# Helper function to create the tables if they don't exist
async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created (if they didn't exist).")

# Helper function to yield the database session
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# ✅ Helper to get the currently active session
async def get_active_session(db: AsyncSession) -> SessionMetrics | None:
    result = await db.execute(select(SessionMetrics).where(SessionMetrics.is_active == True))
    return result.scalar_one_or_none()

# ✅ Main logic for session creation (with single-session enforcement)
async def create_session_db(db: AsyncSession, session_id: str) -> SessionMetrics:
    # Deactivate any other active sessions before starting a new one
    print(f"Checking for existing active sessions to close before starting {session_id}")
    active_sessions_stmt = (
        update(SessionMetrics)
        .where(SessionMetrics.is_active == True)
        .values(
            is_active=False,
            end_time=datetime.now(timezone.utc),
            duration_seconds=func.strftime('%s', datetime.now(timezone.utc)) - func.strftime('%s', SessionMetrics.start_time),
            last_updated=datetime.now(timezone.utc)
        )
    )
    await db.execute(active_sessions_stmt)
    await db.commit()

    # Check if the session already exists
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

    # Create a new session if it doesn't exist
    print(f"Creating new session in DB: {session_id}")
    new_session = SessionMetrics(session_id=session_id)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

# ✅ Update session statistics in the DB
async def update_session_stats_db(db: AsyncSession, session_id: str, superclass: str):
    async with db.begin():
        session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
        session_obj = session.scalar_one_or_none()

        if not session_obj or not session_obj.is_active:
            print(f"Warning: Attempted to update inactive or non-existent session {session_id}")
            return None

        current_stats = session_obj.predictions_by_category if session_obj.predictions_by_category else {}
        current_stats[superclass] = current_stats.get(superclass, 0) + 1

        stmt = (
            update(SessionMetrics)
            .where(SessionMetrics.session_id == session_id)
            .values(
                total_images_processed=SessionMetrics.total_images_processed + 1,
                predictions_by_category=current_stats,
                last_updated=datetime.now(timezone.utc)
            )
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(stmt)

    updated_session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
    return updated_session.scalar_one()

# ✅ Finalize the session in the DB
async def finalize_session_db(db: AsyncSession, session_id: str):
    print(f"Finalizing session in DB: {session_id}")
    async with db.begin():
        session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
        session_obj = session.scalar_one_or_none()

        if not session_obj or not session_obj.is_active:
            print(f"Warning: Session {session_id} already finalized or doesn't exist.")
            return None

        end_time = datetime.now(timezone.utc)
        duration = int((end_time - session_obj.start_time).total_seconds())

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

    print(f"Session {session_id} finalized. Duration: {duration}s")
    finalized_session = await db.execute(select(SessionMetrics).where(SessionMetrics.session_id == session_id))
    return finalized_session.scalar_one()

# ✅ Add a prediction to the database
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
    await db.commit()
    await db.refresh(db_prediction)
    return db_prediction, superclass
