"""
Command execution manager: memastikan hanya satu command aktif per chat.
Command baru akan membatalkan (cancel) command lama yang belum selesai.
"""

import asyncio
import logging
from typing import Callable, Awaitable, Dict, Optional

logger = logging.getLogger(__name__)


class CommandManager:
    """
    Menyimpan task aktif per chat.
    Saat command baru datang: task lama di-cancel dan diganti task baru.
    """

    def __init__(self):
        self._active: Dict[int, asyncio.Task] = {}

    async def run_exclusive(
        self,
        chat_id: int,
        coro_factory: Callable[[], Awaitable],
        on_cancel: Optional[Callable[[], Awaitable]] = None
    ):
        """
        Jalankan coroutine secara eksklusif untuk chat_id.

        Args:
            chat_id: ID chat telegram
            coro_factory: fungsi pembuat coroutine (agar dieksekusi setelah cancel)
            on_cancel: optional callback saat task lama dibatalkan (misal update UI)
        """
        # Cancel previous if still running
        previous = self._active.get(chat_id)
        if previous and not previous.done():
            logger.info("Cancelling previous command for chat_id=%s", chat_id)
            previous.cancel()
            try:
                await previous
            except asyncio.CancelledError:
                logger.debug("Previous command cancelled")
            except Exception as e:
                logger.warning("Previous command raised after cancel: %s", e)
            if on_cancel:
                try:
                    await on_cancel()
                except Exception as e:
                    logger.debug("on_cancel failed: %s", e)

        # Create and store new task
        task = asyncio.create_task(coro_factory())
        self._active[chat_id] = task

        try:
            await task
        except asyncio.CancelledError:
            logger.debug("Current command cancelled by a newer one.")
        except Exception as e:
            logger.error("Unhandled exception in command task: %s", e)

    def cancel_all(self):
        """Optional: Cancel semua task (dipanggil saat shutdown)."""
        for chat_id, task in self._active.items():
            if not task.done():
                task.cancel()

    def is_running(self, chat_id: int) -> bool:
        task = self._active.get(chat_id)
        return bool(task and not task.done())