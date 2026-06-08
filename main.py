from loguru import logger
import asyncio

from db.database import init_db
from parser.telethon_client import start_parser

async def main():
        logger.info("Инициализация БД...")
        await init_db()
        logger.info("БД готова, запускаю парсер...")
        await start_parser()
        logger.success("Парсер запущен!")
    
if __name__ == "__main__":
    asyncio.run(main())