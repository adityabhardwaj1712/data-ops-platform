from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Detect SQLite
IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

# SQLite needs this, others don't
CONNECT_ARGS = {"check_same_thread": False} if IS_SQLITE else {}

# Async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=CONNECT_ARGS,
    pool_pre_ping=True,
)

# Async session factory (PRIMARY)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ✅ BACKWARD-COMPATIBLE ALIAS (THIS FIXES YOUR ERROR)
async_session_factory = AsyncSessionLocal


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


async def get_db():
    """
    FastAPI dependency that provides
    an async DB session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

