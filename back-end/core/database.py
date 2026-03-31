import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Load the variables from the .env file
load_dotenv()

# Grab the database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the async engine
engine = create_async_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite
)

# Create a session factory
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# This is the base class all your future models (like User or Song) will inherit from
class Base(DeclarativeBase):
    pass

# This is the dependency we will inject into our FastAPI routes
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session