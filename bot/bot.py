#!/usr/bin/env python3
"""
Telegram KDE Connect Bot - Pure Python with Reply Keyboard
Version 1.1 - Media, Battery, Network, Process Management
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

import config
from client import SystemClient

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize client
client = SystemClient()


# ===========================
# KEYBOARD LAYOUTS
# ===========================

def main_keyboard():
    """Main menu keyboard - always visible"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='🖥️ System'),
                KeyboardButton(text='🔊 Media'),
            ],
            [
                KeyboardButton(text='📋 Clipboard'),
                KeyboardButton(text='📁 Files'),
            ],
            [
                KeyboardButton(text='🎵 Player'),  # NEW V1.1
                KeyboardButton(text='🌐 Network'),  # NEW V1.1
            ],
            [
                KeyboardButton(text='🔋 Battery'),  # NEW V1.1
                KeyboardButton(text='💻 Processes'),  # NEW V1.1
            ],
            [
                KeyboardButton(text='ℹ️ Status'),
                KeyboardButton(text='❓ Help'),
            ]
        ],
        resize_keyboard=True,
        persistent=True,
        one_time_keyboard=False
    )
    return keyboard


def system_keyboard():
    """System control keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='🔒 Lock Screen'),
                KeyboardButton(text='😴 Sleep'),
            ],
            [
                KeyboardButton(text='📸 Screenshot'),
                KeyboardButton(text='⚠️ Shutdown'),
            ],
            [
                KeyboardButton(text='« Main Menu'),
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def media_keyboard():
    """Media control keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='🔇 Mute'),
                KeyboardButton(text='🔉 25%'),
            ],
            [
                KeyboardButton(text='🔉 50%'),
                KeyboardButton(text='🔊 75%'),
            ],
            [
                KeyboardButton(text='🔊 100%'),
                KeyboardButton(text='« Main Menu'),
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def clipboard_keyboard():
    """Clipboard keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='📋 Get Clipboard'),
                KeyboardButton(text='✍️ Copy Text'),
            ],
            [
                KeyboardButton(text='« Main Menu'),
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def files_keyboard():
    """Files keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='📤 Upload File'),
                KeyboardButton(text='📥 Download File'),
            ],
            [
                KeyboardButton(text='« Main Menu'),
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def player_keyboard():
    """Media player keyboard - NEW V1.1"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='⏮️ Previous'),
                KeyboardButton(text='⏯️ Play/Pause'),
                KeyboardButton(text='⏭️ Next'),
            ],
            [
                KeyboardButton(text='⏹️ Stop'),
                KeyboardButton(text='🎵 Now Playing'),
            ],
            [
                KeyboardButton(text='« Main Menu'),
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def network_keyboard():
    """Network info keyboard - NEW V1.1"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='🌐 Network Info'),
                KeyboardButton(text='📊 Network Stats'),
            ],
            [
                KeyboardButton(text='« Main Menu'),
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def process_keyboard():
    """Process management keyboard - NEW V1.1"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='📊 Top CPU'),
                KeyboardButton(text='💾 Top RAM'),
            ],
            [
                KeyboardButton(text='🔍 Search Process'),
            ],
            [
                KeyboardButton(text='« Main Menu'),
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard


def cancel_keyboard():
    """Cancel keyboard - return to main menu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='❌ Cancel')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


# ===========================
# AUTHORIZATION MIDDLEWARE
# ===========================

async def authorize(message: Message) -> bool:
    """Check if user is authorized"""
    user_id = message.from_user.id

    if user_id != config.OWNER_ID:
        logger.warning(f'⚠️ Unauthorized access attempt from user {user_id}')
        await message.answer('❌ Unauthorized. This bot is for personal use only.')
        return False

    return True


# ===========================
# COMMAND HANDLERS
# ===========================

async def cmd_start(message: Message):
    """Handle /start command"""
    if not await authorize(message):
        return

    await message.answer(
        '🤖 <b>KDE Connect Bot v1.1</b>\n\n'
        'Control your PC from Telegram!\n\n'
        '<b>New in v1.1:</b>\n'
        '🎵 Media Player Control\n'
        '🔋 Battery Monitoring\n'
        '🌐 Network Information\n'
        '💻 Process Management\n\n'
        'Use the keyboard buttons below to navigate.',
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard()
    )


async def cmd_help(message: Message):
    """Handle /help command"""
    if not await authorize(message):
        return

    await message.answer(
        '📖 <b>Help & Commands</b>\n\n'
        '<b>Keyboard Navigation:</b>\n'
        'Use the buttons below for quick access!\n\n'
        '<b>Text Commands:</b>\n'
        '/start - Show main menu\n'
        '/status - System status\n'
        '/battery - Battery status\n'
        '/network - Network info\n'
        '/processes - Process list\n'
        '/volume &lt;0-100&gt; - Set volume\n'
        '/copy &lt;text&gt; - Copy text\n'
        '/help - Show this help\n\n'
        '<b>File Operations:</b>\n'
        'Send any file to upload to PC\n'
        'Send file path to download from PC',
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard()
    )


async def cmd_status(message: Message):
    """Handle /status command"""
    if not await authorize(message):
        return

    msg = await message.answer('🔍 Checking system...')

    try:
        status = await client.get_status()

        if 'hostname' in status:
            text = (
                f"✅ <b>System Online</b>\n\n"
                f"🖥️ Host: <code>{status['hostname']}</code>\n"
                f"💻 OS: <code>{status['os']}</code>\n"
                f"📊 CPU: <code>{status['cpu']}%</code>\n"
                f"💾 RAM: <code>{status['memory']}%</code>\n"
                f"⏱️ Uptime: <code>{status['uptime']}</code>"
            )
        else:
            text = f"❌ {status.get('message', 'Unknown error')}"

        await msg.edit_text(text, parse_mode=ParseMode.HTML)

    except Exception as e:
        await msg.edit_text(f'❌ Error: {str(e)}')


async def cmd_volume(message: Message):
    """Handle /volume command"""
    if not await authorize(message):
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            raise ValueError

        level = int(args[1])
        if level < 0 or level > 100:
            raise ValueError

        msg = await message.answer('⏳ Setting volume...')
        result = await client.send_command('volume', {'level': level})

        icon = '✅' if result.get('status') == 'success' else '❌'
        await msg.edit_text(f"{icon} {result.get('message')}")

    except (IndexError, ValueError):
        await message.answer(
            '❌ Usage: /volume 50 (0-100)',
            reply_markup=media_keyboard()
        )


async def cmd_copy(message: Message):
    """Handle /copy command"""
    if not await authorize(message):
        return

    try:
        text = message.text.replace('/copy', '', 1).strip()
        if not text:
            raise ValueError

        msg = await message.answer('⏳ Copying to clipboard...')
        result = await client.send_command('copy', {'text': text})

        icon = '✅' if result.get('status') == 'success' else '❌'
        await msg.edit_text(f"{icon} {result.get('message')}")

    except ValueError:
        await message.answer(
            '❌ Usage: /copy your text here',
            reply_markup=clipboard_keyboard()
        )


# NEW V1.1 COMMANDS

async def cmd_battery(message: Message):
    """Handle /battery command"""
    if not await authorize(message):
        return

    msg = await message.answer('🔋 Checking battery...')
    result = await client.send_command('battery_status')

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


async def cmd_network(message: Message):
    """Handle /network command"""
    if not await authorize(message):
        return

    msg = await message.answer('🌐 Getting network info...')
    result = await client.send_command('network_info')

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


async def cmd_processes(message: Message):
    """Handle /processes command"""
    if not await authorize(message):
        return

    msg = await message.answer('💻 Getting process list...')
    result = await client.send_command('process_list', {'sort_by': 'cpu', 'limit': 10})

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


# ===========================
# KEYBOARD BUTTON HANDLERS
# ===========================

async def handle_main_menu(message: Message):
    """Return to main menu"""
    await message.answer(
        '📱 <b>Main Menu</b>\n\nSelect an option:',
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard()
    )


async def handle_system_menu(message: Message):
    """Show system menu"""
    await message.answer(
        '🖥️ <b>System Control</b>\n\nChoose an action:',
        parse_mode=ParseMode.HTML,
        reply_markup=system_keyboard()
    )


async def handle_media_menu(message: Message):
    """Show media menu"""
    await message.answer(
        '🔊 <b>Media Control</b>\n\nAdjust volume or mute:',
        parse_mode=ParseMode.HTML,
        reply_markup=media_keyboard()
    )


async def handle_clipboard_menu(message: Message):
    """Show clipboard menu"""
    await message.answer(
        '📋 <b>Clipboard Manager</b>\n\nManage clipboard:',
        parse_mode=ParseMode.HTML,
        reply_markup=clipboard_keyboard()
    )


async def handle_files_menu(message: Message):
    """Show files menu"""
    await message.answer(
        '📁 <b>File Manager</b>\n\nFile operations:',
        parse_mode=ParseMode.HTML,
        reply_markup=files_keyboard()
    )


# NEW V1.1 MENU HANDLERS

async def handle_player_menu(message: Message):
    """Show media player menu"""
    await message.answer(
        '🎵 <b>Media Player</b>\n\nControl playback:',
        parse_mode=ParseMode.HTML,
        reply_markup=player_keyboard()
    )


async def handle_network_menu(message: Message):
    """Show network menu"""
    await message.answer(
        '🌐 <b>Network Information</b>\n\nView network details:',
        parse_mode=ParseMode.HTML,
        reply_markup=network_keyboard()
    )


async def handle_process_menu(message: Message):
    """Show process menu"""
    await message.answer(
        '💻 <b>Process Manager</b>\n\nManage processes:',
        parse_mode=ParseMode.HTML,
        reply_markup=process_keyboard()
    )


# SYSTEM HANDLERS

async def handle_lock_screen(message: Message):
    """Lock screen"""
    msg = await message.answer('🔒 Locking screen...')
    result = await client.send_command('lock')

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(f"{icon} {result.get('message')}")


async def handle_sleep(message: Message):
    """Put PC to sleep"""
    msg = await message.answer('😴 Putting PC to sleep...')
    result = await client.send_command('sleep')

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(f"{icon} {result.get('message')}")


async def handle_screenshot(message: Message):
    """Take screenshot"""
    from aiogram.types import BufferedInputFile

    msg = await message.answer('📸 Taking screenshot...')

    try:
        result = await client.send_command('screenshot')

        if result.get('status') == 'success' and result.get('file'):
            screenshot_data = await client.get_screenshot(result['file'])
            photo = BufferedInputFile(screenshot_data, filename='screenshot.png')
            await message.answer_photo(photo=photo, caption='📸 Screenshot')
            await msg.delete()
        else:
            await msg.edit_text(f"❌ {result.get('message')}")
    except Exception as e:
        await msg.edit_text(f'❌ Error: {str(e)}')


async def handle_shutdown(message: Message):
    """Shutdown PC"""
    await message.answer(
        '⚠️ <b>SHUTDOWN WARNING</b>\n\n'
        'Type <code>/confirm_shutdown</code> to proceed\n'
        'Or press "❌ Cancel" to abort',
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard()
    )


async def handle_confirm_shutdown(message: Message):
    """Confirm shutdown"""
    msg = await message.answer('⚠️ Shutting down...')
    result = await client.send_command('shutdown')

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(
        f"{icon} {result.get('message')}",
        reply_markup=main_keyboard()
    )


# MEDIA HANDLERS

async def handle_mute(message: Message):
    """Toggle mute"""
    msg = await message.answer('🔇 Toggling mute...')
    result = await client.send_command('mute')

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(f"{icon} {result.get('message')}")


async def handle_volume_button(message: Message, level: int):
    """Set volume from button"""
    msg = await message.answer(f'🔊 Setting volume to {level}%...')
    result = await client.send_command('volume', {'level': level})

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(f"{icon} {result.get('message')}")


# CLIPBOARD HANDLERS

async def handle_paste(message: Message):
    """Get clipboard content"""
    msg = await message.answer('📋 Getting clipboard...')

    try:
        result = await client.send_command('paste')
        content = result.get('content', '(empty)')

        await msg.edit_text(
            f"📋 <b>Clipboard Content:</b>\n\n<code>{content}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await msg.edit_text(f'❌ Error: {str(e)}')


async def handle_copy_prompt(message: Message):
    """Prompt for text to copy"""
    await message.answer(
        '✍️ <b>Copy Text to Clipboard</b>\n\n'
        'Send me the text you want to copy:\n\n'
        'Example: <code>Hello World</code>\n'
        'Or use: <code>/copy your text here</code>',
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard()
    )


# FILE HANDLERS

async def handle_upload_prompt(message: Message):
    """Prompt for file upload"""
    await message.answer(
        '📤 <b>Upload File to PC</b>\n\n'
        'Send me any file (document, image, video, etc.) '
        'and I will save it to your PC.',
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard()
    )


async def handle_download_prompt(message: Message):
    """Prompt for file download"""
    await message.answer(
        '📥 <b>Download File from PC</b>\n\n'
        'Send the full file path:\n\n'
        'Example:\n'
        '<code>/home/user/document.pdf</code>\n'
        '<code>C:\\Users\\user\\file.txt</code>',
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard()
    )


# NEW V1.1 HANDLERS

# Media Player Handlers

async def handle_play_pause(message: Message):
    """Toggle play/pause"""
    msg = await message.answer('⏯️ Toggling play/pause...')
    result = await client.send_command('media_play_pause')

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(f"{icon} {result.get('message')}")


async def handle_next(message: Message):
    """Next track"""
    msg = await message.answer('⏭️ Next track...')
    result = await client.send_command('media_next')

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(f"{icon} {result.get('message')}")


async def handle_previous(message: Message):
    """Previous track"""
    msg = await message.answer('⏮️ Previous track...')
    result = await client.send_command('media_previous')

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(f"{icon} {result.get('message')}")


async def handle_stop(message: Message):
    """Stop playback"""
    msg = await message.answer('⏹️ Stopping...')
    result = await client.send_command('media_stop')

    icon = '✅' if result.get('status') == 'success' else '❌'
    await msg.edit_text(f"{icon} {result.get('message')}")


async def handle_now_playing(message: Message):
    """Show now playing"""
    msg = await message.answer('🎵 Getting track info...')
    result = await client.send_command('media_now_playing')

    if result.get('status') == 'success':
        track = result.get('track', 'No track playing')
        status_text = result.get('playback_status', '')
        text = f"🎵 <b>Now Playing</b>\n\n{track}"
        if status_text:
            text += f"\n📊 Status: {status_text}"
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text, parse_mode=ParseMode.HTML)


# Battery Handler

async def handle_battery(message: Message):
    """Show battery status"""
    msg = await message.answer('🔋 Checking battery...')
    result = await client.send_command('battery_status')

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


# Network Handlers

async def handle_network_info(message: Message):
    """Show network info"""
    msg = await message.answer('🌐 Getting network info...')
    result = await client.send_command('network_info')

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


async def handle_network_stats(message: Message):
    """Show network stats"""
    msg = await message.answer('📊 Getting network stats...')
    result = await client.send_command('network_stats')

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


# Process Handlers

async def handle_top_cpu(message: Message):
    """Show top CPU processes"""
    msg = await message.answer('📊 Getting top CPU processes...')
    result = await client.send_command('process_list', {'sort_by': 'cpu', 'limit': 10})

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


async def handle_top_ram(message: Message):
    """Show top RAM processes"""
    msg = await message.answer('💾 Getting top RAM processes...')
    result = await client.send_command('process_list', {'sort_by': 'memory', 'limit': 10})

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


async def handle_search_process_prompt(message: Message):
    """Prompt for process search"""
    await message.answer(
        '🔍 <b>Search Process</b>\n\n'
        'Send the process name to search:\n\n'
        'Example: <code>chrome</code> or <code>firefox</code>',
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard()
    )


async def handle_cancel(message: Message):
    """Cancel current operation"""
    await message.answer(
        '❌ Cancelled',
        reply_markup=main_keyboard()
    )


# FILE UPLOAD/DOWNLOAD HANDLERS

async def handle_document(message: Message):
    """Handle document upload"""
    if not await authorize(message):
        return

    msg = await message.answer('📥 Uploading file to PC...')

    try:
        file = await message.bot.get_file(message.document.file_id)
        file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"

        result = await client.upload_file(
            filename=message.document.file_name,
            file_url=file_url,
            file_size=message.document.file_size
        )

        if result.get('status') == 'success':
            await msg.edit_text(
                f"✅ <b>File Uploaded</b>\n\n📁 <code>{result.get('path')}</code>",
                parse_mode=ParseMode.HTML
            )
        else:
            await msg.edit_text(f"❌ {result.get('message')}")
    except Exception as e:
        await msg.edit_text(f'❌ Error: {str(e)}')


async def handle_photo(message: Message):
    """Handle photo upload"""
    if not await authorize(message):
        return

    msg = await message.answer('📸 Saving photo to PC...')

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"

        filename = f'photo_{int(message.date.timestamp())}.jpg'

        result = await client.upload_file(
            filename=filename,
            file_url=file_url,
            file_size=photo.file_size
        )

        if result.get('status') == 'success':
            await msg.edit_text(
                f"✅ <b>Photo Saved</b>\n\n📁 <code>{result.get('path')}</code>",
                parse_mode=ParseMode.HTML
            )
        else:
            await msg.edit_text(f"❌ {result.get('message')}")
    except Exception as e:
        await msg.edit_text(f'❌ Error: {str(e)}')


async def handle_text(message: Message):
    """Handle text messages"""
    if not await authorize(message):
        return

    from aiogram.types import BufferedInputFile
    import os

    text = message.text

    # Check if it looks like a file path
    if '/' in text or '\\' in text:
        msg = await message.answer('📥 Retrieving file from PC...')

        try:
            file_data = await client.download_file(text)
            filename = os.path.basename(text)

            document = BufferedInputFile(file_data, filename=filename)
            await message.answer_document(document=document)
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f'❌ Error: {str(e)}')
    else:
        # Assume it's text to copy
        msg = await message.answer('⏳ Copying to clipboard...')
        result = await client.send_command('copy', {'text': text})

        icon = '✅' if result.get('status') == 'success' else '❌'
        await msg.edit_text(f"{icon} {result.get('message')}")


# ===========================
# MAIN FUNCTION
# ===========================

async def main():
    """Main function to start the bot"""

    # Banner
    print('\n' + '=' * 60)
    print('🤖 Telegram KDE Connect Bot v1.1 - Reply Keyboard')
    print('=' * 60)
    print(f'👤 Owner: {config.OWNER_ID}')
    print(f'🔗 Client: {config.CLIENT_URL}')
    print(f'🔑 Auth: {config.AUTH_TOKEN[:10]}...{config.AUTH_TOKEN[-5:]}')
    print('\n🆕 Version 1.1 Features:')
    print('   ✅ Media player control')
    print('   ✅ Battery monitoring')
    print('   ✅ Network information')
    print('   ✅ Process management')
    print('=' * 60)
    print('\n📡 Starting bot with long polling...\n')

    # Initialize bot
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Register command handlers
    dp.message.register(cmd_start, Command('start', 'menu'))
    dp.message.register(cmd_help, Command('help'))
    dp.message.register(cmd_status, Command('status'))
    dp.message.register(cmd_volume, Command('volume'))
    dp.message.register(cmd_copy, Command('copy'))
    dp.message.register(cmd_battery, Command('battery'))
    dp.message.register(cmd_network, Command('network'))
    dp.message.register(cmd_processes, Command('processes'))
    dp.message.register(handle_confirm_shutdown, Command('confirm_shutdown'))

    # Register menu button handlers
    dp.message.register(handle_main_menu, F.text == '« Main Menu')
    dp.message.register(handle_system_menu, F.text == '🖥️ System')
    dp.message.register(handle_media_menu, F.text == '🔊 Media')
    dp.message.register(handle_clipboard_menu, F.text == '📋 Clipboard')
    dp.message.register(handle_files_menu, F.text == '📁 Files')

    # NEW V1.1 Menu Buttons
    dp.message.register(handle_player_menu, F.text == '🎵 Player')
    dp.message.register(handle_network_menu, F.text == '🌐 Network')
    dp.message.register(handle_process_menu, F.text == '💻 Processes')

    # System buttons
    dp.message.register(handle_lock_screen, F.text == '🔒 Lock Screen')
    dp.message.register(handle_sleep, F.text == '😴 Sleep')
    dp.message.register(handle_screenshot, F.text == '📸 Screenshot')
    dp.message.register(handle_shutdown, F.text == '⚠️ Shutdown')

    # Media buttons
    dp.message.register(handle_mute, F.text == '🔇 Mute')
    dp.message.register(lambda m: handle_volume_button(m, 25), F.text == '🔉 25%')
    dp.message.register(lambda m: handle_volume_button(m, 50), F.text == '🔉 50%')
    dp.message.register(lambda m: handle_volume_button(m, 75), F.text == '🔊 75%')
    dp.message.register(lambda m: handle_volume_button(m, 100), F.text == '🔊 100%')

    # Clipboard buttons
    dp.message.register(handle_paste, F.text == '📋 Get Clipboard')
    dp.message.register(handle_copy_prompt, F.text == '✍️ Copy Text')

    # File buttons
    dp.message.register(handle_upload_prompt, F.text == '📤 Upload File')
    dp.message.register(handle_download_prompt, F.text == '📥 Download File')

    # NEW V1.1 Button Handlers

    # Player buttons
    dp.message.register(handle_play_pause, F.text == '⏯️ Play/Pause')
    dp.message.register(handle_next, F.text == '⏭️ Next')
    dp.message.register(handle_previous, F.text == '⏮️ Previous')
    dp.message.register(handle_stop, F.text == '⏹️ Stop')
    dp.message.register(handle_now_playing, F.text == '🎵 Now Playing')

    # Battery button
    dp.message.register(handle_battery, F.text == '🔋 Battery')

    # Network buttons
    dp.message.register(handle_network_info, F.text == '🌐 Network Info')
    dp.message.register(handle_network_stats, F.text == '📊 Network Stats')

    # Process buttons
    dp.message.register(handle_top_cpu, F.text == '📊 Top CPU')
    dp.message.register(handle_top_ram, F.text == '💾 Top RAM')
    dp.message.register(handle_search_process_prompt, F.text == '🔍 Search Process')

    # Other buttons
    dp.message.register(cmd_status, F.text == 'ℹ️ Status')
    dp.message.register(cmd_help, F.text == '❓ Help')
    dp.message.register(handle_cancel, F.text == '❌ Cancel')

    # File handlers
    dp.message.register(handle_document, F.document)
    dp.message.register(handle_photo, F.photo)

    # Text handler (last, catch-all)
    dp.message.register(handle_text, F.text & ~F.text.startswith('/'))

    # Start polling
    try:
        logger.info('✅ Bot started successfully!')
        logger.info('📱 Send /start to your bot on Telegram')
        logger.info('⌨️ Reply keyboard will appear at bottom of chat')
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f'❌ Error: {e}')
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n👋 Bot stopped by user')
        sys.exit(0)
    except Exception as e:
        logger.error(f'❌ Fatal error: {e}')
        sys.exit(1)