import asyncio

from db.database import init_db
from parser.telethon_client import start_parser

async def main():
        print("Инициализация БД...")
        await init_db()
        print("БД готова, запускаю парсер...")
        await start_parser()
        print("Парсер запущен!")
    
if __name__ == "__main__":
    asyncio.run(main())