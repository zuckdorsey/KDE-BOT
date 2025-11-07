import asyncio
import pytest

from bot.command_manager import CommandManager

@pytest.mark.asyncio
async def test_exclusive_cancels_previous():
    cm = CommandManager()
    order = []

    async def long_task(name):
        order.append(f"start:{name}")
        try:
            await asyncio.sleep(0.5)
            order.append(f"end:{name}")
        except asyncio.CancelledError:
            order.append(f"cancel:{name}")
            raise

    async def run1():
        await cm.run_exclusive(chat_id=1, coro_factory=lambda: long_task('A'))

    async def run2():
        await cm.run_exclusive(chat_id=1, coro_factory=lambda: long_task('B'))

    t1 = asyncio.create_task(run1())
    await asyncio.sleep(0.1)
    t2 = asyncio.create_task(run2())
    await asyncio.gather(t1, t2)

    # Ensure A was cancelled and B completed
    assert any(e.startswith('cancel:A') for e in order)
    assert 'end:B' in order
