"""
HTTP Client to communicate with local Flask server
"""

import aiohttp
import logging
from typing import Dict, Optional, Any
import config

logger = logging.getLogger(__name__)


class SystemClient:
    """Async HTTP client for Flask server communication"""

    def __init__(self):
        self.base_url = config.CLIENT_URL
        self.auth_token = config.AUTH_TOKEN
        self.timeout = aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }

    async def send_command(self, command: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send command to Flask server

        Args:
            command: Command name (lock, volume, screenshot, etc)
            params: Optional parameters

        Returns:
            Response dict with status and message
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                        f'{self.base_url}/command',
                        json={'command': command, 'params': params or {}},
                        headers=self.headers
                ) as response:
                    if response.status == 401:
                        return {
                            'status': 'error',
                            'message': 'Authentication failed. Check AUTH_TOKEN.'
                        }

                    response.raise_for_status()
                    return await response.json()

        except aiohttp.ClientConnectorError:
            logger.error('Cannot connect to Python client')
            return {
                'status': 'error',
                'message': 'Python client not running.\n\nStart it with:\ncd client && python server.py'
            }
        except aiohttp.ClientTimeout:
            logger.error('Request timeout')
            return {
                'status': 'error',
                'message': 'Request timeout. Try again.'
            }
        except Exception as e:
            logger.error(f'Request failed: {e}')
            return {
                'status': 'error',
                'message': f'Request failed: {str(e)}'
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                        f'{self.base_url}/status',
                        headers=self.headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f'Failed to get status: {e}')
            return {'status': 'error', 'message': str(e)}

    async def upload_file(self, filename: str, file_url: str, file_size: int) -> Dict[str, Any]:
        """Upload file to PC"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                        f'{self.base_url}/upload',
                        json={'filename': filename, 'url': file_url, 'size': file_size},
                        headers=self.headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f'Upload failed: {e}')
            return {'status': 'error', 'message': str(e)}

    async def download_file(self, filepath: str) -> bytes:
        """Download file from PC"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                        f'{self.base_url}/getfile',
                        json={'path': filepath},
                        headers=self.headers
                ) as response:
                    response.raise_for_status()
                    return await response.read()
        except Exception as e:
            logger.error(f'Download failed: {e}')
            raise Exception(f'Download failed: {str(e)}')

    async def get_screenshot(self, filename: str) -> bytes:
        """Get screenshot file"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                        f'{self.base_url}/download/{filename}',
                        headers=self.headers
                ) as response:
                    response.raise_for_status()
                    return await response.read()
        except Exception as e:
            logger.error(f'Screenshot download failed: {e}')
            raise Exception(f'Screenshot download failed: {str(e)}')