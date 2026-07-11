"""Утилиты для работы с VK API (через vkbottle)."""
from __future__ import annotations

from loguru import logger
from vkbottle import API
from vkbottle.exception_factory import VKAPIError

from config import settings

# Один общий экземпляр API на весь парсер
api: API | None = None


def get_api() -> API:
    global api
    if api is None:
        if not settings.VK_TOKEN:
            raise RuntimeError("VK_TOKEN не задан в .env")
        api = API(settings.VK_TOKEN)
    return api


async def resolve_group_id(group: int | str) -> int:
    """Принимает id (число) или short-имя (строка), возвращает отрицательный id группы."""
    if isinstance(group, int):
        return -abs(group)

    # Строка — пробуем как число, иначе резолвим через utils.resolveScreenName
    group = group.strip()
    if group.lstrip("-").isdigit():
        return -abs(int(group))

    if group.startswith(("https://vk.com/", "vk.com/")):
        group = group.split("/")[-1]

    vk = get_api()
    try:
        resp = await vk.utils.resolve_screen_name(screen_name=group.lstrip("@"))
        if resp.type == "group" and resp.object_id:
            return -abs(resp.object_id)
        if resp.type == "page" and resp.object_id:
            return -abs(resp.object_id)
    except VKAPIError as e:
        logger.error(f"Не удалось резолвить группу '{group}': {e}")
    raise ValueError(f"Не удалось определить group_id для '{group}'")


async def get_user_info(user_id: int) -> dict:
    """Возвращает {first_name, last_name, screen_name} по id пользователя."""
    vk = get_api()
    try:
        users = await vk.users.get(user_ids=user_id, fields="screen_name")
        if users:
            u = users[0]
            return {
                "first_name": u.first_name or "",
                "last_name": u.last_name or "",
                "screen_name": getattr(u, "screen_name", None) or f"id{u.id}",
            }
    except VKAPIError as e:
        logger.debug(f"users.get failed for {user_id}: {e}")
    return {}


async def get_group_info(group_id: int) -> dict:
    """Возвращает {name, screen_name} по id группы."""
    vk = get_api()
    try:
        groups = await vk.groups.get_by_id(group_id=abs(group_id))
        if groups:
            g = groups[0]
            return {
                "name": getattr(g, "name", "") or "",
                "screen_name": getattr(g, "screen_name", "") or f"club{abs(group_id)}",
            }
    except VKAPIError as e:
        logger.debug(f"groups.getById failed for {group_id}: {e}")
    return {}


def full_name(info: dict) -> str:
    parts = [info.get("first_name", ""), info.get("last_name", "")]
    return " ".join(p for p in parts if p).strip()