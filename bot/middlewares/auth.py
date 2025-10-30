"""
Authorization middleware for aiogram
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import config
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware to check user authorization"""

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """Check if user is authorized"""

        # Get user from event
        if isinstance(event, Message):
            user_id = event.from_user.id
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            chat_id = event.message.chat.id
        else:
            return await handler(event, data)

        # Check authorization
        if user_id != config.OWNER_ID:
            logger.warning(f'⚠️ Unauthorized access attempt from user {user_id}')

            if isinstance(event, Message):
                await event.answer('❌ Unauthorized. This bot is for personal use only.')
            elif isinstance(event, CallbackQuery):
                await event.answer('❌ Unauthorized', show_alert=True)

            return

        # User is authorized, proceed
        return await handler(event, data)