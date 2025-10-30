#!/usr/bin/env python3
"""
Quick start script for bot
"""

import sys
import os

# Add bot directory to path
sys.path.insert(0, os.path.dirname(__file__))

from bot import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n👋 Bot stopped by user')
        sys.exit(0)
    except Exception as e:
        print(f'\n❌ Fatal error: {e}')
        sys.exit(1)