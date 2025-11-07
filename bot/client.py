"""
HTTP Client to communicate with local Flask server
Enhanced with retries, backoff, and clearer error messages.
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Optional, Any, Callable, Awaitable
from . import config

logger = logging.getLogger(__name__)


class SystemClient:
    """Async HTTP client for Flask server communication with retry/backoff."""

    def __init__(self):
        self.base_url = config.CLIENT_URL.rstrip("/")
        self.auth_token = config.AUTH_TOKEN
        self.timeout = aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
        # Retry config (exponential backoff)
        self._max_attempts = 3
        self._base_backoff = 0.25  # seconds
        self._session: Optional[aiohttp.ClientSession] = None  # persistent session

    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy-create a persistent aiohttp session reused across requests."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def aclose(self):
        """Close underlying session (called on bot shutdown)."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _with_retries(self, func: Callable[[], Awaitable[Any]]) -> Any:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                return await func()
            except (aiohttp.ClientConnectorError, aiohttp.ServerTimeoutError, asyncio.TimeoutError) as e:
                last_exc = e
                logger.warning("Request attempt %d/%d failed: %s", attempt, self._max_attempts, e)
                if attempt < self._max_attempts:
                    backoff = self._base_backoff * (2 ** (attempt - 1))
                    await asyncio.sleep(backoff)
            except Exception as e:
                last_exc = e
                break
        if last_exc:
            raise last_exc

    async def send_command(self, command: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send command to Flask server and return JSON response with robust error handling.
        """
        url = f'{self.base_url}/command'
        payload = {'command': command, 'params': params or {}}

        async def _do():
            session = await self._get_session()
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 401:
                    return {'status': 'error', 'message': 'Authentication failed. Check AUTH_TOKEN on bot and client.'}
                if response.status >= 500:
                    text = await response.text()
                    logger.error("Server error %s: %s", response.status, text)
                    return {'status': 'error', 'message': 'Local client error (5xx). Try again.'}
                response.raise_for_status()
                return await response.json()

        try:
            return await self._with_retries(_do)
        except aiohttp.ClientConnectorError:
            return {'status': 'error', 'message': 'Python client not running.\nStart: cd client && python server.py'}
        except asyncio.TimeoutError:
            return {'status': 'error', 'message': 'Request timeout. Please try again.'}
        except Exception as e:
            logger.error('Request failed: %s', e)
            return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}

    async def get_status(self) -> Dict[str, Any]:
        """Get system status with retries."""
        url = f'{self.base_url}/status'

        async def _do():
            session = await self._get_session()
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()

        try:
            return await self._with_retries(_do)
        except Exception as e:
            logger.error('Failed to get status: %s', e)
            return {'status': 'error', 'message': str(e)}

    async def upload_file(self, filename: str, file_url: str, file_size: int) -> Dict[str, Any]:
        """Upload file to PC, returning server JSON response."""
        url = f'{self.base_url}/upload'
        payload = {'filename': filename, 'url': file_url, 'size': file_size}

        async def _do():
            session = await self._get_session()
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 401:
                    return {'status': 'error', 'message': 'Authentication failed for upload.'}
                response.raise_for_status()
                return await response.json()

        try:
            return await self._with_retries(_do)
        except Exception as e:
            logger.error('Upload failed: %s', e)
            return {'status': 'error', 'message': str(e)}

    async def download_file(self, filepath: str) -> bytes:
        """Download file bytes from PC. Raises Exception on error (handled by caller)."""
        url = f'{self.base_url}/getfile'
        payload = {'path': filepath}

        async def _do():
            session = await self._get_session()
            async with session.post(url, json=payload, headers=self.headers) as response:
                response.raise_for_status()
                return await response.read()

        return await self._with_retries(_do)

    async def get_screenshot(self, filename: str) -> bytes:
        """Get screenshot file bytes. Raises Exception on error (handled by caller)."""
        url = f'{self.base_url}/download/{filename}'

        async def _do():
            session = await self._get_session()
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.read()

        return await self._with_retries(_do)