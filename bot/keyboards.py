"""
Inline keyboard layouts for aiogram bot
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
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
            InlineKeyboardButton(text='🎵 Player', callback_data='menu_player'),  # NEW
            InlineKeyboardButton(text='🌐 Network', callback_data='menu_network')  # NEW
        ],
        [
            InlineKeyboardButton(text='🔋 Battery', callback_data='cmd_battery'),  # NEW
            InlineKeyboardButton(text='💻 Processes', callback_data='menu_processes')  # NEW
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

def player_menu() -> InlineKeyboardMarkup:
    """Media player control menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='⏮️ Previous', callback_data='media_previous'),
            InlineKeyboardButton(text='⏯️ Play/Pause', callback_data='media_play_pause'),
            InlineKeyboardButton(text='⏭️ Next', callback_data='media_next')
        ],
        [
            InlineKeyboardButton(text='⏹️ Stop', callback_data='media_stop'),
            InlineKeyboardButton(text='🎵 Now Playing', callback_data='media_now_playing')
        ],
        [InlineKeyboardButton(text='« Back to Menu', callback_data='menu_main')]
    ])


def network_menu() -> InlineKeyboardMarkup:
    """Network information menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🌐 Network Info', callback_data='cmd_network_info'),
            InlineKeyboardButton(text='📊 Network Stats', callback_data='cmd_network_stats')
        ],
        [InlineKeyboardButton(text='« Back to Menu', callback_data='menu_main')]
    ])


def processes_menu() -> InlineKeyboardMarkup:
    """Process manager menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='📊 Top CPU', callback_data='proc_list_cpu'),
            InlineKeyboardButton(text='💾 Top RAM', callback_data='proc_list_mem')
        ],
        [
            InlineKeyboardButton(text='🔍 Search Process', callback_data='proc_search_prompt'),
            InlineKeyboardButton(text='❌ Kill Process', callback_data='proc_kill_prompt')
        ],
        [InlineKeyboardButton(text='« Back to Menu', callback_data='menu_main')]
    ])