from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase # New


# Строка подключения для SQLite
DATABASE_URL = "sqlite:///ecommerce.db"

# Создаём Engine
engine = create_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
SessionLocal = sessionmaker(bind=engine)


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DB_URL = "postgresql+asyncpg://ecommerce_user:1234@localhost:5432/ecommerce_db"

async_engine = create_async_engine(DB_URL, echo=True)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):  # New
    pass