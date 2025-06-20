import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Text
from sqlalchemy.exc import OperationalError
import asyncio

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@postgres:5432/handler_db",
)

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text)

async def init_db(retries: int = 5, delay: float = 2) -> None:
    """Initialise database tables, retrying if the DB isn't ready yet."""
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except OperationalError:
            if attempt == retries:
                raise
            await asyncio.sleep(delay)
