#!/usr/bin/env python3
"""
Telegram KDE Connect Bot - Enhanced with CommandManager (exclusive commands)
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode, ChatAction

import config
from client import SystemClient
from middlewares.error import ErrorMiddleware
from utils import safe_edit, safe_delete, chat_action, result_icon, ephemeral_notice
from command_manager import CommandManager  # NEW

from fallbacks import fallback_callback

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

client = SystemClient()
command_manager = CommandManager()  # NEW


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🖥️ System'), KeyboardButton(text='🔊 Media')],
            [KeyboardButton(text='📋 Clipboard'), KeyboardButton(text='📁 Files')],
            [KeyboardButton(text='🎵 Player'), KeyboardButton(text='🌐 Network')],
            [KeyboardButton(text='🔋 Battery'), KeyboardButton(text='💻 Processes')],
            [KeyboardButton(text='ℹ️ Status'), KeyboardButton(text='❓ Help')],
        ],
        resize_keyboard=True,
        persistent=True,
        one_time_keyboard=False
    )


def system_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🔒 Lock Screen'), KeyboardButton(text='😴 Sleep')],
            [KeyboardButton(text='📸 Screenshot'), KeyboardButton(text='⚠️ Shutdown')],
            [KeyboardButton(text='« Main Menu')],
        ],
        resize_keyboard=True,
        persistent=True
    )


def media_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🔇 Mute'), KeyboardButton(text='🔉 25%')],
            [KeyboardButton(text='🔉 50%'), KeyboardButton(text='🔊 75%')],
            [KeyboardButton(text='🔊 100%'), KeyboardButton(text='« Main Menu')],
        ],
        resize_keyboard=True,
        persistent=True
    )


def clipboard_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📋 Get Clipboard'), KeyboardButton(text='✍️ Copy Text')],
            [KeyboardButton(text='« Main Menu')],
        ],
        resize_keyboard=True,
        persistent=True
    )


def files_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📤 Upload File'), KeyboardButton(text='📥 Download File')],
            [KeyboardButton(text='« Main Menu')],
        ],
        resize_keyboard=True,
        persistent=True
    )


async def authorize(message: Message) -> bool:
    if message.from_user.id != config.OWNER_ID:
        await message.answer('❌ Unauthorized.')
        return False
    return True


async def cmd_start(message: Message):
    if not await authorize(message):
        return
    await message.answer(
        '🤖 <b>KDE Connect Bot</b>\n\nExclusive command mode aktif.\nKirim perintah baru akan membatalkan yang lama.',
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard()
    )


async def cmd_status(message: Message):
    if not await authorize(message):
        return

    async def runner():
        msg = await message.answer('🔍 Checking system...')
        async with chat_action(message.bot, message.chat.id, ChatAction.TYPING):
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
        await safe_edit(msg, text, parse_mode=ParseMode.HTML)

    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Perintah sebelumnya dibatalkan.")
    )


async def handle_screenshot(message: Message):
    if not await authorize(message):
        return

    from aiogram.types import BufferedInputFile

    async def runner():
        msg = await message.answer('📸 Taking screenshot...')
        async with chat_action(message.bot, message.chat.id, ChatAction.UPLOAD_PHOTO):
            result = await client.send_command('screenshot')
            if result.get('status') == 'success' and result.get('file'):
                data = await client.get_screenshot(result['file'])
                photo = BufferedInputFile(data, filename='screenshot.png')
                await message.answer_photo(photo=photo, caption='📸 Screenshot')
                await safe_delete(msg)
            else:
                await safe_edit(msg, f"❌ {result.get('message')}")

    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Screenshot lama diabaikan.")
    )


async def handle_lock_screen(message: Message):
    if not await authorize(message):
        return

    async def runner():
        msg = await message.answer('🔒 Locking screen...')
        result = await client.send_command('lock')
        await safe_edit(msg, f"{result_icon(result.get('status'))} {result.get('message')}")

    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Lock sebelumnya dibatalkan.")
    )


async def handle_volume_button(message: Message, level: int):
    if not await authorize(message):
        return

    async def runner():
        msg = await message.answer(f'🔊 Setting volume {level}%...')
        result = await client.send_command('volume', {'level': level})
        await safe_edit(msg, f"{result_icon(result.get('status'))} {result.get('message')}")

    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Perintah volume sebelumnya di-cancel.")
    )


async def handle_copy_prompt(message: Message):
    await message.answer(
        '✍️ Kirim teks untuk disalin ke clipboard.\nPerintah baru membatalkan proses copy sebelumnya.',
        reply_markup=clipboard_keyboard()
    )


async def handle_paste(message: Message):
    if not await authorize(message):
        return

    async def runner():
        msg = await message.answer('📋 Getting clipboard...')
        result = await client.send_command('paste')
        content = result.get('content', '(empty)')
        await safe_edit(msg, f"📋 <b>Clipboard:</b>\n<code>{content}</code>", parse_mode=ParseMode.HTML)

    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Paste sebelumnya dibatalkan.")
    )


async def cmd_volume(message: Message):
    if not await authorize(message):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer('❌ Usage: /volume 50', reply_markup=media_keyboard())
        return
    try:
        level = int(parts[1])
        if not 0 <= level <= 100:
            raise ValueError
    except ValueError:
        await message.answer('❌ Volume harus antara 0-100.')
        return
    await handle_volume_button(message, level)

async def handle_sleep(message: Message):
    """
    Put PC to sleep (exclusive). Membatalkan perintah sleep sebelumnya jika user spam.
    """
    if not await authorize(message):
        return

    async def runner():
        msg = await message.answer('😴 Putting PC to sleep...')
        result = await client.send_command('sleep')
        await safe_edit(msg, f"{result_icon(result.get('status'))} {result.get('message')}")

    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Sleep sebelumnya dibatalkan.")
    )

async def cmd_copy(message: Message):
    if not await authorize(message):
        return
    text = message.text.replace('/copy', '', 1).strip()
    if not text:
        await message.answer('❌ Usage: /copy your text')
        return

    async def runner():
        msg = await message.answer('⏳ Copying...')
        result = await client.send_command('copy', {'text': text})
        await safe_edit(msg, f"{result_icon(result.get('status'))} {result.get('message')}")

    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Copy sebelumnya dibatalkan.")
    )


async def handle_shutdown(message: Message):
    if not await authorize(message):
        return
    async def runner():
        msg = await message.answer('⚠️ Shutting down...')
        result = await client.send_command('shutdown')
        await safe_edit(msg, f"{result_icon(result.get('status'))} {result.get('message')}",
                        reply_markup=main_keyboard())
    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Shutdown lama dibatalkan.")
    )

async def handle_mute(message: Message):
    """
    Toggle mute (exclusive). Jika user kirim perintah mute berulang, hanya yang terakhir diproses.
    """
    if not await authorize(message):
        return

    async def runner():
        msg = await message.answer('🔇 Toggling mute...')
        result = await client.send_command('mute')
        await safe_edit(msg, f"{result_icon(result.get('status'))} {result.get('message')}")

    await command_manager.run_exclusive(
        chat_id=message.chat.id,
        coro_factory=runner,
        on_cancel=lambda: ephemeral_notice(message, "⏳ Mute sebelumnya dibatalkan.")
    )
async def handle_main_menu(message: Message):
    await message.answer('📱 <b>Main Menu</b>', parse_mode=ParseMode.HTML, reply_markup=main_keyboard())


async def handle_system_menu(message: Message):
    await message.answer('🖥️ <b>System Control</b>', parse_mode=ParseMode.HTML, reply_markup=system_keyboard())


async def handle_media_menu(message: Message):
    await message.answer('🔊 <b>Media Control</b>', parse_mode=ParseMode.HTML, reply_markup=media_keyboard())


async def handle_clipboard_menu(message: Message):
    await message.answer('📋 <b>Clipboard</b>', parse_mode=ParseMode.HTML, reply_markup=clipboard_keyboard())


async def handle_files_menu(message: Message):
    await message.answer('📁 <b>Files</b>', parse_mode=ParseMode.HTML, reply_markup=files_keyboard())


async def main():
    print('\n' + '=' * 60)
    print('🤖 KDE Connect Bot - Exclusive Command Mode')
    print('=' * 60)
    print(f'Owner: {config.OWNER_ID}')
    print(f'Client: {config.CLIENT_URL}')
    print('=' * 60)

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Global error middleware
    dp.message.middleware(ErrorMiddleware())

    # Register commands
    dp.message.register(cmd_start, Command('start'))
    dp.message.register(cmd_status, Command('status'))
    dp.message.register(cmd_volume, Command('volume'))
    dp.message.register(cmd_copy, Command('copy'))

    # Menus
    dp.message.register(handle_main_menu, F.text == '« Main Menu')
    dp.message.register(handle_system_menu, F.text == '🖥️ System')
    dp.message.register(handle_media_menu, F.text == '🔊 Media')
    dp.message.register(handle_clipboard_menu, F.text == '📋 Clipboard')
    dp.message.register(handle_files_menu, F.text == '📁 Files')

    # Actions
    dp.message.register(handle_lock_screen, F.text == '🔒 Lock Screen')
    dp.message.register(handle_sleep, F.text == '😴 Sleep')
    dp.message.register(handle_screenshot, F.text == '📸 Screenshot')
    dp.message.register(handle_shutdown, F.text == '⚠️ Shutdown')

    dp.message.register(handle_mute, F.text == '🔇 Mute')
    dp.message.register(lambda m: handle_volume_button(m, 25), F.text == '🔉 25%')
    dp.message.register(lambda m: handle_volume_button(m, 50), F.text == '🔉 50%')
    dp.message.register(lambda m: handle_volume_button(m, 75), F.text == '🔊 75%')
    dp.message.register(lambda m: handle_volume_button(m, 100), F.text == '🔊 100%')

    dp.message.register(handle_paste, F.text == '📋 Get Clipboard')
    dp.message.register(handle_copy_prompt, F.text == '✍️ Copy Text')

    dp.callback_query.register(fallback_callback)

    try:
        logger.info("Bot started with long polling")
        await dp.start_polling(bot)
    finally:
        command_manager.cancel_all()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Exit")
        sys.exit(0)