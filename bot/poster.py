import html

from loguru import logger
from aiogram import Bot

from config import settings

from db.models import Lead, VkLead, VkMessageLead
from aiogram.client.session.aiohttp import AiohttpSession

bot = Bot(token=settings.BOT_TOKEN, session=AiohttpSession(timeout=60))


def _contact_line(display: str | None, url: str | None, phone: str | None) -> str:
    """Юзернейм кликабельной ссылкой, если его нет — телефон.

    Оба поля пустыми быть не должны: источники сами скипают такие лиды до
    сохранения в БД, это чисто defensive-ветка на случай будущих изменений.
    """
    if display:
        label = html.escape(display)
        return f'🔗 <a href="{html.escape(url)}">{label}</a>' if url else f"🔗 {label}"
    if phone:
        return f"📞 {html.escape(phone)}"
    return "🔗 —"


def format_lead(lead: Lead) -> str:
    name = html.escape(lead.tg_name) if lead.tg_name else "—"
    contact = _contact_line(
        f"@{lead.sender_username}" if lead.sender_username else None,
        f"https://t.me/{lead.sender_username}" if lead.sender_username else None,
        lead.phone,
    )
    chat_title = html.escape(lead.chat_title or lead.chat_id)
    chat = f'<a href="{html.escape(lead.chat_link)}">{chat_title}</a>' if lead.chat_link else chat_title
    return (
        f"🆕 <b>Заявка из Telegram</b>\n\n"
        f"{html.escape(lead.text)}\n\n"
        f"👤 {name}\n"
        f"{contact}\n"
        f"💬 {chat}"
    )


def format_vk_lead(lead: VkLead) -> str:
    name = html.escape(lead.author_name) if lead.author_name else "—"
    contact = _contact_line(
        lead.author_screen_name,
        f"https://vk.com/{lead.author_screen_name}" if lead.author_screen_name else None,
        lead.author_phone,
    )
    source_label = "Комментарий" if lead.source_type == "comment" else "Пост"
    post_link = f"https://vk.com/wall{lead.group_id}_{lead.post_id}"
    if lead.source_type == "comment":
        post_link += f"?reply={lead.comment_id}"
    group_name = html.escape(lead.group_name or f"club{abs(lead.group_id)}")
    return (
        f"🆕 <b>Заявка из VK</b>\n\n"
        f"{html.escape(lead.text)}\n\n"
        f"👤 {name}\n"
        f"{contact}\n"
        f'💬 <a href="{post_link}">{source_label}: {group_name}</a>'
    )


def format_vk_message_lead(lead: VkMessageLead) -> str:
    name = html.escape(lead.sender_name) if lead.sender_name else "—"
    contact = _contact_line(
        lead.sender_screen_name,
        f"https://vk.com/{lead.sender_screen_name}" if lead.sender_screen_name else None,
        lead.sender_phone,
    )
    if lead.source_type == "chat":
        label = html.escape(lead.chat_title) if lead.chat_title else f"Беседа #{lead.chat_id}"
    else:
        label = "Личные сообщения"
    # Deep-link в раздел "Сообщения сообщества" на конкретный диалог/беседу.
    conv_link = f"https://vk.com/gim{lead.group_id}?sel={lead.peer_id}"
    return (
        f"🆕 <b>Заявка из VK</b>\n\n"
        f"{html.escape(lead.text)}\n\n"
        f"👤 {name}\n"
        f"{contact}\n"
        f'💬 <a href="{conv_link}">{label}</a>'
    )


async def post_lead(lead: Lead):
    logger.info("Отправляю в канал...")
    text = format_lead(lead)
    try:
        await bot.send_message(settings.CHANNEL_ID, text, parse_mode="HTML", disable_web_page_preview=True)
        logger.success("Отправлено!")
    except Exception as e:
        logger.warning(f"Ошибка: {e}")


async def post_vk_lead(lead: VkLead):
    logger.info("Отправляю VK-лид в канал...")
    text = format_vk_lead(lead)
    try:
        await bot.send_message(settings.CHANNEL_ID, text, parse_mode="HTML", disable_web_page_preview=True)
        logger.success("Отправлено!")
    except Exception as e:
        logger.warning(f"Ошибка: {e}")


async def post_vk_message_lead(lead: VkMessageLead):
    logger.info("Отправляю VK-сообщение в канал...")
    text = format_vk_message_lead(lead)
    try:
        await bot.send_message(settings.CHANNEL_ID, text, parse_mode="HTML", disable_web_page_preview=True)
        logger.success("Отправлено!")
    except Exception as e:
        logger.warning(f"Ошибка: {e}")
