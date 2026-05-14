import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from api.config import config


engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    from api.models import User

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.username == config.EXPERT_USERNAME))
        if result.scalar_one_or_none():
            return
        try:
            user = User(
                username=config.EXPERT_USERNAME,
                password_hash=bcrypt.hashpw(config.EXPERT_PASSWORD.encode(), bcrypt.gensalt()).decode(),
            )
            session.add(user)
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
