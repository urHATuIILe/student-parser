"""Загрузка списков мониторинга (чаты/группы/беседы) из targets.yaml.

Отделено от config.py: там — секреты и параметры окружения (.env),
здесь — предметные списки целей, которые меняются независимо от них.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from loguru import logger

_TARGETS_PATH = Path(__file__).resolve().parent / "targets.yaml"


def _normalize(value: int | str) -> int | str:
    if isinstance(value, int):
        return value
    value = str(value).strip()
    try:
        return int(value)
    except ValueError:
        return value


def _load_raw() -> dict:
    if not _TARGETS_PATH.exists():
        logger.warning(f"{_TARGETS_PATH.name} не найден — списки чатов/групп пусты")
        return {}
    with _TARGETS_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_raw = _load_raw()
_telegram = _raw.get("telegram") or {}
_vk = _raw.get("vk") or {}

TELEGRAM_CHATS: list[int | str] = [_normalize(c) for c in (_telegram.get("chats") or [])]
VK_GROUPS: list[int | str] = [_normalize(g) for g in (_vk.get("groups") or [])]
VK_CHATS: list[int] = [int(c) for c in (_vk.get("chats") or [])]
