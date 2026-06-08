from telethon import TelegramClient, events
from config import settings

from parser.classifier import is_tutor_request

from db.models import Lead
from db.database import save_lead

from bot.poster import post_lead

client = TelegramClient('session/parser', settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)

@client.on(events.NewMessage(chats=settings.chats_list))
async def on_new_message(event):
    print(f"chat_id: {event.chat_id}")
    print(f"Новое сообщение: {event.message.text}")
    text = event.message.text
    if not is_tutor_request(text):
        return 
    
    sender = await event.get_sender()
    message_id = event.message.id
    chat_id = event.chat_id
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
    
    await save_lead(lead)
    await post_lead(lead)
    
async def start_parser():
    print("Подключаюсь к Telegram...")
    print(f"Чаты для мониторинга: {settings.chats_list}")
    await client.start()
    print("Подключился! Слушаю чаты...")
    await client.run_until_disconnected()