"""Парсинг постов со стены VK-группы."""
from __future__ import annotations

from datetime import datetime
from loguru import logger
from vkbottle.exception_factory import VKAPIError

from config import settings
from targets import VK_GROUPS
from parser.classifier import is_tutor_request
from parser.vk_utils import get_api, resolve_group_id, get_user_info, get_group_info, full_name
from db.models import VkLead
from db.database import save_vk_lead, is_vk_duplicate, mark_vk_lead_posted
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

        # Автор поста. Если пост от имени самой группы (from_id < 0) — контактов
        # нет, писать некому, такой лид бесполезен и пропускается.
        from_id = getattr(item, "from_id", None) or getattr(item, "signer_id", None)
        if not isinstance(from_id, int) or from_id <= 0:
            continue

        info = await get_user_info(from_id)
        if not info:
            continue
        author_name = full_name(info) or None
        author_screen = info.get("screen_name")
        author_phone = info.get("phone")
        if not author_screen and not author_phone:
            logger.info(f"У автора поста {post_id} нет ни ника, ни телефона — пропускаю")
            continue

        group_info = await get_group_info(owner_id)

        lead = VkLead(
            post_id=post_id,
            group_id=owner_id,
            comment_id=None,
            author_id=from_id,
            author_name=author_name,
            author_screen_name=author_screen,
            author_phone=author_phone,
            group_name=group_info.get("name"),
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
            await mark_vk_lead_posted(lead.id)
        except Exception as e:
            logger.error(f"Ошибка постинга VK-лида: {e}")

    return created


async def parse_all_groups_posts() -> list[VkLead]:
    """Парсит посты во всех группах из настроек."""
    all_created: list[VkLead] = []
    for group in VK_GROUPS:
        try:
            created = await parse_group_posts(group)
            all_created.extend(created)
        except Exception as e:
            logger.error(f"Ошибка при парсинге постов группы {group}: {e}")
    return all_created