"""Парсинг личных сообщений, присланных сообществу VK, через LongPoll Bot API.

В отличие от vk_posts/vk_comments (которые опрашивают стену по списку VK_GROUPS),
здесь можно слушать только то сообщество, которому принадлежит VK_TOKEN — LongPoll
диалогов привязан к конкретной группе, а не к произвольному списку групп.
"""
from __future__ import annotations

from loguru import logger
from vkbottle.bot import Bot, Message

from config import settings
from parser.classifier import is_tutor_request
from parser.vk_utils import get_user_info, full_name
from db.models import VkDialogLead
from db.database import save_vk_dialog_lead, is_vk_dialog_duplicate, mark_vk_dialog_lead_posted
from bot.poster import post_vk_dialog_lead

bot = Bot(token=settings.VK_TOKEN) if settings.VK_TOKEN else None

_group_id: int | None = None


async def _get_own_group_id() -> int:
    """id сообщества, которому принадлежит VK_TOKEN (кешируется на процесс)."""
    global _group_id
    if _group_id is None:
        response = await bot.api.groups.get_by_id()
        if not response.groups:
            raise RuntimeError("Не удалось определить group_id для VK_TOKEN")
        _group_id = response.groups[0].id
    return _group_id


if bot is not None:
    @bot.on.message()
    async def handle_dialog_message(message: Message) -> None:
        text = (message.text or "").strip()
        if not text or not is_tutor_request(text):
            return

        group_id = await _get_own_group_id()
        message_id = message.id
        if await is_vk_dialog_duplicate(message_id, group_id):
            logger.debug(f"Дубль сообщения {message_id} в диалогах, пропускаю")
            return

        sender_id = message.from_id
        sender_name = None
        sender_screen = None
        if sender_id and sender_id > 0:
            info = await get_user_info(sender_id)
            sender_name = full_name(info) or None
            sender_screen = info.get("screen_name")

        lead = VkDialogLead(
            message_id=message_id,
            group_id=group_id,
            sender_id=sender_id,
            sender_name=sender_name,
            sender_screen_name=sender_screen,
            text=text,
        )

        try:
            await save_vk_dialog_lead(lead)
            logger.success(f"Сохранено VK-сообщение {message_id} от {sender_id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения VK-сообщения: {e}")
            return

        try:
            await post_vk_dialog_lead(lead)
            await mark_vk_dialog_lead_posted(lead.id)
        except Exception as e:
            logger.error(f"Ошибка постинга VK-сообщения: {e}")


async def start_vk_dialogs_parser() -> None:
    if bot is None:
        logger.warning("VK_TOKEN не задан — парсер VK-диалогов не запущен")
        return
    logger.info("Подключаюсь к LongPoll сообщества VK...")
    await bot.run_polling()
