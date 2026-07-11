"""Парсинг постов со стены VK-группы."""
from __future__ import annotations

from datetime import datetime
from loguru import logger
from vkbottle.exception_factory import VKAPIError

from config import settings
from parser.classifier import is_tutor_request
from parser.vk_utils import get_api, resolve_group_id, get_user_info, full_name
from db.models import VkLead
from db.database import save_vk_lead, is_vk_duplicate
from bot.poster import post_vk_lead


async def parse_group_posts(group: int | str) -> list[VkLead]:
    """Парсит последние посты группы, возвращает список созданных VkLead."""
    vk = get_api()
    try:
        owner_id = await resolve_group_id(group)
    except Exception as e:
        logger.error(f"Пропускаю группу {group}: {e}")
        return []

    try:
        wall = await vk.wall.get(
            owner_id=owner_id,
            count=settings.VK_POSTS_PER_POLL,
            filter="owner",
        )
    except VKAPIError as e:
        logger.error(f"wall.get для группы {owner_id} не удался: {e}")
        return []

    created: list[VkLead] = []

    for item in wall.items:
        text = (item.text or "").strip()
        if not text or not is_tutor_request(text):
            continue

        post_id = item.id
        if await is_vk_duplicate(post_id, owner_id, comment_id=None):
            logger.debug(f"Дубль поста {post_id} в группе {owner_id}, пропускаю")
            continue

        # Автор поста
        from_id = getattr(item, "from_id", None) or getattr(item, "signer_id", None)
        author_name = None
        author_screen = None
        author_id_db = None
        if isinstance(from_id, int) and from_id > 0:
            author_id_db = from_id
            info = await get_user_info(from_id)
            author_name = full_name(info) or None
            author_screen = info.get("screen_name")

        lead = VkLead(
            post_id=post_id,
            group_id=owner_id,
            comment_id=None,
            author_id=author_id_db,
            author_name=author_name,
            author_screen_name=author_screen,
            text=text,
            source_type="post",
            parsed_at=datetime.utcnow(),
        )

        try:
            await save_vk_lead(lead)
            created.append(lead)
            logger.success(f"Сохранён VK-пост {post_id} из группы {owner_id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения VK-поста: {e}")
            continue

        try:
            await post_vk_lead(lead)
        except Exception as e:
            logger.error(f"Ошибка постинга VK-лида: {e}")

    return created


async def parse_all_groups_posts() -> list[VkLead]:
    """Парсит посты во всех группах из настроек."""
    all_created: list[VkLead] = []
    for group in settings.vk_groups_list:
        try:
            created = await parse_group_posts(group)
            all_created.extend(created)
        except Exception as e:
            logger.error(f"Ошибка при парсинге постов группы {group}: {e}")
    return all_created