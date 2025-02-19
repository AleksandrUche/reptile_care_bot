from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

from config_data.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, future=True, echo=False)

async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base: DeclarativeMeta = declarative_base()
