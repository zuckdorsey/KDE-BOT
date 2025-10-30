"""
Configuration for aiogram bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID', 0))

# Client Configuration
CLIENT_URL = os.getenv('CLIENT_URL', 'http://127.0.0.1:5000')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

# Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is required in .env file")

if not OWNER_ID:
    raise ValueError("❌ OWNER_ID is required in .env file")

if not AUTH_TOKEN:
    raise ValueError("❌ AUTH_TOKEN is required in .env file")

print("✅ Configuration loaded successfully")