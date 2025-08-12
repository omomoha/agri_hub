from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=True,  # Set to False in production
    pool_pre_ping=True,
    pool_recycle=300,
)

# Dependency to get database session
def get_session():
    with Session(engine) as session:
        yield session

# Create database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
