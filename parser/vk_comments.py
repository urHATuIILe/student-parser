"""Парсинг комментариев под постами VK-группы."""
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


async def _parse_comments_for_post(owner_id: int, post_id: int) -> list[VkLead]:
    """Парсит комментарии под конкретным постом."""
    vk = get_api()
    try:
        comments = await vk.wall.get_comments(
            owner_id=owner_id,
            post_id=post_id,
            count=settings.VK_COMMENTS_PER_POST,
            sort="desc",
        )
    except VKAPIError as e:
        logger.debug(f"wall.getComments для поста {post_id} не удался: {e}")
        return []

    created: list[VkLead] = []

    items = getattr(comments, "items", []) or []
    for item in items:
        text = (getattr(item, "text", "") or "").strip()
        if not text or not is_tutor_request(text):
            continue

        comment_id = item.id
        if await is_vk_duplicate(post_id, owner_id, comment_id=comment_id):
            logger.debug(f"Дубль комментария {comment_id} под постом {post_id}, пропускаю")
            continue

        from_id = getattr(item, "from_id", None)
        if not isinstance(from_id, int) or from_id <= 0:
            continue

        info = await get_user_info(from_id)
        if not info:
            continue
        author_name = full_name(info) or None
        author_screen = info.get("screen_name")
        author_phone = info.get("phone")
        if not author_screen and not author_phone:
            logger.info(f"У автора комментария {comment_id} нет ни ника, ни телефона — пропускаю")
            continue

        group_info = await get_group_info(owner_id)

        lead = VkLead(
            post_id=post_id,
            group_id=owner_id,
            comment_id=comment_id,
            author_id=from_id,
            author_name=author_name,
            author_screen_name=author_screen,
            author_phone=author_phone,
            group_name=group_info.get("name"),
            text=text,
            source_type="comment",
            parsed_at=datetime.utcnow(),
        )

        try:
            await save_vk_lead(lead)
            created.append(lead)
            logger.success(
                f"Сохранён VK-комментарий {comment_id} под постом {post_id} (группа {owner_id})"
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения VK-комментария: {e}")
            continue

        try:
            await post_vk_lead(lead)
            await mark_vk_lead_posted(lead.id)
        except Exception as e:
            logger.error(f"Ошибка постинга VK-комментария: {e}")

    return created


async def parse_group_comments(group: int | str) -> list[VkLead]:
    """Парсит комментарии под последними постами группы."""
    vk = get_api()
    try:
        owner_id = await resolve_group_id(group)
    except Exception as e:
        logger.error(f"Пропускаю комментарии группы {group}: {e}")
        return []

    try:
        wall = await vk.wall.get(
            owner_id=owner_id,
            count=settings.VK_POSTS_FOR_COMMENTS,
            filter="owner",
        )
    except VKAPIError as e:
        logger.error(f"wall.get (для комментариев) группы {owner_id} не удался: {e}")
        return []

    all_created: list[VkLead] = []
    for item in wall.items:
        post_id = item.id
        try:
            created = await _parse_comments_for_post(owner_id, post_id)
            all_created.extend(created)
        except Exception as e:
            logger.error(f"Ошибка парсинга комментариев под постом {post_id}: {e}")

    return all_created


async def parse_all_groups_comments() -> list[VkLead]:
    """Парсит комментарии во всех группах из настроек."""
    all_created: list[VkLead] = []
    for group in VK_GROUPS:
        try:
            created = await parse_group_comments(group)
            all_created.extend(created)
        except Exception as e:
            logger.error(f"Ошибка при парсинге комментариев группы {group}: {e}")
    return all_created