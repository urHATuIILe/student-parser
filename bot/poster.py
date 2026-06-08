from aiogram import Bot

from config import settings

from db.models import Lead
from aiohttp import ClientSession
from aiogram.client.session.aiohttp import AiohttpSession

bot = Bot(token=settings.BOT_TOKEN, session=AiohttpSession(timeout=60))


def format_lead(lead: Lead) -> str:
     return (
        f" {lead.text}\n\n"
        f" @{lead.sender_username}\n"
        f"Чат: {lead.chat_id}"
    )
    
    
async def post_lead(lead: Lead):
    print("Отправляю в канал...")
    text = format_lead(lead)
    try:
        await bot.send_message(settings.CHANNEL_ID, text)
        print("Отправлено!")
    except Exception as e:
        print(f"Ошибка: {e}")