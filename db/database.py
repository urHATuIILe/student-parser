from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import settings
from db.models import Base, Lead

engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False )

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def close_db():
    await engine.dispose()
    

async def save_lead(lead: Lead):
    async with AsyncSessionFactory() as session:
        session.add(lead)
        await session.commit()
        
async def is_duplicate(message_id: int, chat_id: str) -> bool:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(exists().where(
                Lead.message_id == message_id,
                Lead.chat_id == chat_id,                
            ))
        )
        return result.scalar()
    