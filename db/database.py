from sqlalchemy import select, exists, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import settings
from db.models import Base, Lead, VkLead, VkDialogLead

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

async def mark_lead_posted(lead_id: int):
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(Lead).where(Lead.id == lead_id).values(is_posted=True)
        )
        await session.commit()


# ===== VK =====

async def save_vk_lead(lead: VkLead):
    async with AsyncSessionFactory() as session:
        session.add(lead)
        await session.commit()

async def is_vk_duplicate(post_id: int, group_id: int, comment_id: int | None = None) -> bool:
    async with AsyncSessionFactory() as session:
        if comment_id is None:
            result = await session.execute(
                select(exists().where(
                    VkLead.post_id == post_id,
                    VkLead.group_id == group_id,
                    VkLead.comment_id.is_(None),
                ))
            )
        else:
            result = await session.execute(
                select(exists().where(
                    VkLead.post_id == post_id,
                    VkLead.group_id == group_id,
                    VkLead.comment_id == comment_id,
                ))
            )
        return result.scalar()

async def mark_vk_lead_posted(lead_id: int):
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(VkLead).where(VkLead.id == lead_id).values(is_posted=True)
        )
        await session.commit()


# ===== VK: личные сообщения сообществу =====

async def save_vk_dialog_lead(lead: VkDialogLead):
    async with AsyncSessionFactory() as session:
        session.add(lead)
        await session.commit()

async def is_vk_dialog_duplicate(message_id: int, group_id: int) -> bool:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(exists().where(
                VkDialogLead.message_id == message_id,
                VkDialogLead.group_id == group_id,
            ))
        )
        return result.scalar()

async def mark_vk_dialog_lead_posted(lead_id: int):
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(VkDialogLead).where(VkDialogLead.id == lead_id).values(is_posted=True)
        )
        await session.commit()
