"""
Utility helpers (ditambahkan helper baru optional).
"""

import asyncio
import contextlib
import logging
from typing import Optional
from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.types import Message

logger = logging.getLogger(__name__)


async def safe_edit(message: Message, text: str, **kwargs) -> None:
    with contextlib.suppress(TelegramBadRequest, TelegramAPIError):
        await message.edit_text(text, **kwargs)


async def safe_delete(message: Message) -> None:
    with contextlib.suppress(TelegramBadRequest, TelegramAPIError):
        await message.delete()


class chat_action:
    def __init__(self, bot: Bot, chat_id: int, action: ChatAction) -> None:
        self.bot = bot
        self.chat_id = chat_id
        self.action = action

    async def __aenter__(self):
        try:
            await self.bot.send_chat_action(chat_id=self.chat_id, action=self.action)
        except Exception:
            pass

    async def __aexit__(self, exc_type, exc, tb):
        return False


def result_icon(status: Optional[str]) -> str:
    return '✅' if status == 'success' else '❌'


async def ephemeral_notice(message: Message, text: str, delay: float = 2.5):
    """
    Kirim pesan sementara lalu hapus sendiri (dipakai saat cancel).
    """
    try:
        m = await message.answer(text)
        await asyncio.sleep(delay)
        await safe_delete(m)
    except Exception:
        pass