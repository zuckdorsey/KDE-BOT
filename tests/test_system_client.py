import asyncio
import pytest

from bot.client import SystemClient

@pytest.mark.asyncio
async def test_system_client_handles_unreachable(monkeypatch):
    client = SystemClient()

    async def failing():
        raise ConnectionRefusedError

    # Monkeypatch _with_retries to run failing coroutine
    with pytest.raises(ConnectionRefusedError):
        await client._with_retries(lambda: failing())

    await client.aclose()
