from loguru import logger
from aiogram import Bot

from config import settings

from db.models import Lead, VkLead
from aiogram.client.session.aiohttp import AiohttpSession

bot = Bot(token=settings.BOT_TOKEN, session=AiohttpSession(timeout=60))


def format_lead(lead: Lead) -> str:
    username = f"@{lead.sender_username}" if lead.sender_username else "—"
    return (
        f"🆕 Заявка из Telegram\n\n"
        f"{lead.text}\n\n"
        f"👤 {lead.tg_name or '—'}\n"
        f"🔗 {username}\n"
        f"Чат: {lead.chat_id}"
    )


def format_vk_lead(lead: VkLead) -> str:
    author = f"vk.com/{lead.author_screen_name}" if lead.author_screen_name else "—"
    name = lead.author_name or "—"
    source = "Комментарий" if lead.source_type == "comment" else "Пост"
    return (
        f"🆕 Заявка из VK ({source})\n\n"
        f"{lead.text}\n\n"
        f"👤 {name}\n"
        f"🔗 {author}\n"
        f"Группа: vk.com/club{abs(lead.group_id)}"
    )


async def post_lead(lead: Lead):
    logger.info("Отправляю в канал...")
    text = format_lead(lead)
    try:
        await bot.send_message(settings.CHANNEL_ID, text)
        logger.success("Отправлено!")
    except Exception as e:
        logger.warning(f"Ошибка: {e}")


async def post_vk_lead(lead: VkLead):
    logger.info("Отправляю VK-лид в канал...")
    text = format_vk_lead(lead)
    try:
        await bot.send_message(settings.CHANNEL_ID, text)
        logger.success("Отправлено!")
    except Exception as e:
        logger.warning(f"Ошибка: {e}")