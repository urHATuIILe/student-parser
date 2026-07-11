"""Оркестратор VK-парсера: периодический polling постов и комментариев."""
from __future__ import annotations

import asyncio

from loguru import logger

from config import settings
from parser.vk_utils import get_api
from parser.vk_posts import parse_all_groups_posts
from parser.vk_comments import parse_all_groups_comments


async def _vk_polling_cycle() -> None:
    """Один цикл опроса: посты + комментарии."""
    logger.info("🔄 VK: начинаю цикл парсинга постов...")
    posts = await parse_all_groups_posts()
    logger.info(f"VK: новых постов-лидов: {len(posts)}")

    logger.info("🔄 VK: начинаю цикл парсинга комментариев...")
    comments = await parse_all_groups_comments()
    logger.info(f"VK: новых комментариев-лидов: {len(comments)}")


async def start_vk_parser() -> None:
    """Бесконечный цикл polling'а VK с заданным интервалом."""
    if not settings.VK_TOKEN:
        logger.warning("VK_TOKEN не задан — VK-парсер не запущен")
        return
    if not settings.vk_groups_list:
        logger.warning("VK_GROUPS не задан — VK-парсер не запущен")
        return

    # Инициализируем API заранее, чтобы отвалиться сразу при неверном токене
    try:
        get_api()
        logger.success("VK API инициализирован")
    except Exception as e:
        logger.error(f"Не удалось инициализировать VK API: {e}")
        return

    interval = max(60, settings.VK_POLLING_INTERVAL)
    logger.info(
        f"VK-парсер запущен. Группы: {settings.vk_groups_list}. "
        f"Интервал опроса: {interval} сек."
    )

    # Первый прогон сразу при старте
    try:
        await _vk_polling_cycle()
    except Exception as e:
        logger.error(f"Ошибка в цикле VK-парсинга: {e}")

    while True:
        try:
            await asyncio.sleep(interval)
            await _vk_polling_cycle()
        except asyncio.CancelledError:
            logger.info("VK-парсер остановлен")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка VK-парсера: {e}")
            await asyncio.sleep(interval)