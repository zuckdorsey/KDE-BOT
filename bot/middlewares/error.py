"""
Global error middleware to handle unexpected exceptions gracefully.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import logging

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    """Catch unhandled exceptions from handlers and notify the user."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            # Log full stack trace for debugging
            logger.exception("Unhandled error while processing event: %s", e)

            # Try to inform the user nicely
            try:
                if isinstance(event, Message):
                    await event.answer("❌ Terjadi kesalahan tak terduga. Silakan coba lagi.")
                elif isinstance(event, CallbackQuery):
                    # Show alert if callback
                    await event.answer("❌ Terjadi kesalahan tak terduga.", show_alert=True)
            except Exception:
                # Avoid recursive failures
                pass

            # Swallow exception (already logged and user informed)
            return