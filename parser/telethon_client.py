from loguru import logger
from telethon import TelegramClient, events
from config import settings
from targets import TELEGRAM_CHATS

from parser.classifier import is_tutor_request

from db.models import Lead
from db.database import save_lead, is_duplicate, mark_lead_posted
from bot.poster import post_lead


client = TelegramClient('session/parser', settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)


def build_chat_link(chat, chat_id: int, message_id: int) -> str | None:
    """Ссылка на сообщение в чате. Публичный чат — по юзернейму, приватный
    супергруппа/канал — через t.me/c/<internal_id> (работает только для них,
    у обычных небольших групп такой ссылки в принципе не существует)."""
    username = getattr(chat, "username", None)
    if username:
        return f"https://t.me/{username}/{message_id}"

    marked_id = str(chat_id)
    if marked_id.startswith("-100"):
        internal_id = marked_id[4:]
        return f"https://t.me/c/{internal_id}/{message_id}"
    return None


@client.on(events.NewMessage(chats=TELEGRAM_CHATS))
async def on_new_message(event):
    logger.info(f"chat_id: {event.chat_id}")
    logger.info(f"Новое сообщение: {event.message.text}")
    text = event.message.text
    if not is_tutor_request(text):
        return 
    
    sender = await event.get_sender()
    message_id = event.message.id
    chat_id = event.chat_id
    if await is_duplicate(message_id, str(chat_id)):
        logger.info("Дубль, пропускаю")
        return
    username = sender.username if sender else None
    tg_name = sender.first_name if sender else None
    phone = sender.phone if sender else None

    if not username and not phone:
        logger.info("Нет ни юзернейма, ни телефона — пропускаю, связаться не с кем")
        return

    chat = await event.get_chat()
    chat_title = getattr(chat, "title", None) or str(chat_id)
    chat_link = build_chat_link(chat, chat_id, message_id)

    lead = Lead(
        message_id = message_id,
        chat_id = str(chat_id),
        chat_title = chat_title,
        chat_link = chat_link,
        sender_username = username,
        tg_name = tg_name,
        text = text,
        phone=phone,
    )
    
    try:
        await save_lead(lead)
        logger.success("Сообщение сохранено")
    except Exception as e:
        logger.error(f"Ошибка сохранения в БД {e}")
    
    try:
        await post_lead(lead)
        await mark_lead_posted(lead.id)
    except Exception as e:
        logger.error(f"Ошибка постинга {e}")
    
async def start_parser():
    logger.info("Подключаюсь к Telegram...")
    logger.info(f"Чаты для мониторинга: {TELEGRAM_CHATS}")
    await client.start()
    logger.success("Подключился! Слушаю чаты...")
    await client.run_until_disconnected()