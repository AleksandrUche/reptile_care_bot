from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config_data.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
