from loguru import logger
from telethon import TelegramClient, events
from config import settings

from parser.classifier import is_tutor_request

from db.models import Lead
from db.database import save_lead, is_duplicate
from bot.poster import post_lead


client = TelegramClient('session/parser', settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)

@client.on(events.NewMessage(chats=settings.chats_list))
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
    
    lead = Lead(
        message_id = message_id,
        chat_id = str(chat_id),
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
    except Exception as e:
        logger.error(f"Ошибка постинга {e}")
    
async def start_parser():
    logger.info("Подключаюсь к Telegram...")
    logger.info(f"Чаты для мониторинга: {settings.chats_list}")
    await client.start()
    logger.success("Подключился! Слушаю чаты...")
    await client.run_until_disconnected()