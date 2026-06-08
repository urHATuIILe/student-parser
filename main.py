from loguru import logger
import asyncio

from db.database import init_db
from parser.telethon_client import start_parser

async def main():
    logger.info("Инициализация БД...")
    await init_db()
    logger.info("БД готова, запускаю парсер...")
    try:
        await start_parser()
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
    finally:
        logger.info("Завершение работы...")
        
if __name__ == "__main__":
    asyncio.run(main())