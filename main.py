from loguru import logger
import asyncio

from db.database import init_db, close_db
from parser.telethon_client import start_parser
from parser.vk_messages import start_vk_parser
from parser.vk_inbox import start_vk_inbox_parser


async def main():
    logger.info("Инициализация БД...")
    await init_db()
    logger.info("БД готова, запускаю парсеры (Telegram + VK)...")

    # Запускаем все парсеры параллельно
    tasks = [
        asyncio.create_task(start_parser(), name="telegram_parser"),
        asyncio.create_task(start_vk_parser(), name="vk_wall_parser"),
        asyncio.create_task(start_vk_inbox_parser(), name="vk_inbox_parser"),
    ]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Остановка вручную")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
    finally:
        for t in tasks:
            if not t.done():
                t.cancel()
        await close_db()
        logger.info("Завершение работы...")


if __name__ == "__main__":
    asyncio.run(main())