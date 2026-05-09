# These are sync imports

# from sqlalchemy import create_engine
# from sqlalchemy.orm import DeclarativeBase, sessionmaker

# These are async imports
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# NOTE : Sync code is commeted out

# SQLALCHEMY_DB_URL = 'sqlite:///./blog.db'
SQLALCHEMY_DB_URL = 'sqlite+aiosqlite:///./blog.db'

# engine = create_engine(
#     SQLALCHEMY_DB_URL,
#     connect_args={"check_same_thread" : False}
# )
engine = create_async_engine(
    SQLALCHEMY_DB_URL,
    connect_args={"check_same_thread" : False}
)


# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
    
async def get_db():
    async with AyncSessionLocal() as session:
        yield session