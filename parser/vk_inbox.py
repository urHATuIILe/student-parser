"""Входящие сообщения VK через LongPoll Bot API: личные сообщения сообществу и беседы.

Личные диалоги (peer_id == user_id) ловим все, без белого списка — сам факт
сообщения сообществу уже целевой сигнал. Беседы (peer_id >= 2_000_000_000,
куда сообщество добавлено участником) фильтруем по targets.VK_CHATS, чтобы не
разгребать все чаты подряд, если бот состоит в них не только по делу.
"""
from __future__ import annotations

from loguru import logger
from vkbottle.bot import Bot, Message

from config import settings
from targets import VK_CHATS
from parser.classifier import is_tutor_request
from parser.vk_utils import get_user_info, full_name
from db.models import VkMessageLead
from db.database import save_vk_message_lead, is_vk_message_duplicate, mark_vk_message_lead_posted
from bot.poster import post_vk_message_lead

CHAT_PEER_OFFSET = 2_000_000_000

bot = Bot(token=settings.VK_TOKEN) if settings.VK_TOKEN else None


async def _get_chat_title(peer_id: int) -> str | None:
    try:
        response = await bot.api.messages.get_conversations_by_id(peer_ids=[peer_id])
        if response.items and response.items[0].chat_settings:
            return response.items[0].chat_settings.title
    except Exception as e:
        logger.debug(f"Не удалось получить название беседы {peer_id}: {e}")
    return None


if bot is not None:
    @bot.on.message()
    async def handle_message(message: Message) -> None:
        text = (message.text or "").strip()
        if not text or not is_tutor_request(text):
            return

        peer_id = message.peer_id
        is_chat = peer_id >= CHAT_PEER_OFFSET
        chat_id = peer_id - CHAT_PEER_OFFSET if is_chat else None

        if is_chat and chat_id not in VK_CHATS:
            return

        conversation_message_id = message.conversation_message_id
        if await is_vk_message_duplicate(peer_id, conversation_message_id):
            logger.debug(f"Дубль сообщения {conversation_message_id} в peer {peer_id}, пропускаю")
            return

        # Без опознанного отправителя писать некому — такой лид бесполезен.
        sender_id = message.from_id
        if not sender_id or sender_id <= 0:
            return

        info = await get_user_info(sender_id)
        if not info:
            return
        sender_name = full_name(info) or None
        sender_screen = info.get("screen_name")
        sender_phone = info.get("phone")
        if not sender_screen and not sender_phone:
            logger.info(f"У отправителя {sender_id} нет ни ника, ни телефона — пропускаю")
            return

        chat_title = await _get_chat_title(peer_id) if is_chat else None

        lead = VkMessageLead(
            peer_id=peer_id,
            conversation_message_id=conversation_message_id,
            group_id=message.group_id,
            chat_id=chat_id,
            chat_title=chat_title,
            source_type="chat" if is_chat else "dialog",
            sender_id=sender_id,
            sender_name=sender_name,
            sender_screen_name=sender_screen,
            sender_phone=sender_phone,
            text=text,
        )

        try:
            await save_vk_message_lead(lead)
            logger.success(f"Сохранено VK-сообщение (peer {peer_id}) от {sender_id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения VK-сообщения: {e}")
            return

        try:
            await post_vk_message_lead(lead)
            await mark_vk_message_lead_posted(lead.id)
        except Exception as e:
            logger.error(f"Ошибка постинга VK-сообщения: {e}")


async def start_vk_inbox_parser() -> None:
    if bot is None:
        logger.warning("VK_TOKEN не задан — парсер VK-сообщений не запущен")
        return
    logger.info(f"Подключаюсь к LongPoll сообщества VK. Беседы в whitelist: {VK_CHATS}")
    await bot.run_polling()
