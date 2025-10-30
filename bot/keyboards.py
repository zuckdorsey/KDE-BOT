"""
Inline keyboard layouts for aiogram bot
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🖥️ System', callback_data='menu_system'),
            InlineKeyboardButton(text='🔊 Media', callback_data='menu_media')
        ],
        [
            InlineKeyboardButton(text='📋 Clipboard', callback_data='menu_clipboard'),
            InlineKeyboardButton(text='📁 Files', callback_data='menu_files')
        ],
        [
            InlineKeyboardButton(text='ℹ️ Status', callback_data='cmd_status'),
            InlineKeyboardButton(text='🔄 Refresh', callback_data='menu_main')
        ]
    ])


def system_menu() -> InlineKeyboardMarkup:
    """Create system control menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🔒 Lock Screen', callback_data='cmd_lock'),
            InlineKeyboardButton(text='😴 Sleep', callback_data='cmd_sleep')
        ],
        [
            InlineKeyboardButton(text='📸 Screenshot', callback_data='cmd_screenshot'),
            InlineKeyboardButton(text='⚠️ Shutdown', callback_data='cmd_shutdown_warn')
        ],
        [InlineKeyboardButton(text='« Back to Menu', callback_data='menu_main')]
    ])


def media_menu() -> InlineKeyboardMarkup:
    """Create media control menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🔇 Mute', callback_data='cmd_mute'),
            InlineKeyboardButton(text='🔉 25%', callback_data='cmd_vol_25')
        ],
        [
            InlineKeyboardButton(text='🔉 50%', callback_data='cmd_vol_50'),
            InlineKeyboardButton(text='🔊 75%', callback_data='cmd_vol_75')
        ],
        [
            InlineKeyboardButton(text='🔊 100%', callback_data='cmd_vol_100'),
            InlineKeyboardButton(text='« Back', callback_data='menu_main')
        ]
    ])


def clipboard_menu() -> InlineKeyboardMarkup:
    """Create clipboard menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='📋 Get Clipboard', callback_data='cmd_paste'),
            InlineKeyboardButton(text='✍️ Copy Text', callback_data='cmd_copy_prompt')
        ],
        [InlineKeyboardButton(text='« Back to Menu', callback_data='menu_main')]
    ])


def files_menu() -> InlineKeyboardMarkup:
    """Create files menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='📤 Upload File', callback_data='cmd_upload_prompt'),
            InlineKeyboardButton(text='📥 Download File', callback_data='cmd_download_prompt')
        ],
        [InlineKeyboardButton(text='« Back to Menu', callback_data='menu_main')]
    ])


def shutdown_confirm() -> InlineKeyboardMarkup:
    """Create shutdown confirmation menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='✅ Yes, Shutdown', callback_data='cmd_shutdown'),
            InlineKeyboardButton(text='❌ Cancel', callback_data='menu_system')
        ]
    ])