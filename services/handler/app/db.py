import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Text, select
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


class HighScore(Base):
    __tablename__ = "highscores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    score: Mapped[int] = mapped_column(Integer, default=0)

async def init_db(retries: int = 5, delay: float = 2) -> None:
    """Initialise database tables, retrying if the DB isn't ready yet."""
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            async with SessionLocal() as session:
                result = await session.execute(select(HighScore))
                hs = result.scalar_one_or_none()
                if hs is None:
                    session.add(HighScore(score=0))
                    await session.commit()
            break
        except OperationalError:
            if attempt == retries:
                raise
            await asyncio.sleep(delay)
