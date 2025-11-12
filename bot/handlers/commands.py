"""
Command handlers for aiogram bot
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

import keyboards
from client import SystemClient

router = Router()
client = SystemClient()


@router.message(Command('start', 'menu'))
async def cmd_start(message: Message):
    """Handle /start and /menu commands"""
    await message.answer(
        '🤖 <b>KDE Connect Bot</b>\n\n'
        'Control your PC via Telegram with buttons!\n\n'
        'Choose a category below:',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.main_menu()
    )


@router.message(Command('help'))
async def cmd_help(message: Message):
    """Handle /help command"""
    await message.answer(
        '📖 <b>Help & Commands</b>\n\n'
        '<b>Text Commands:</b>\n'
        '/start - Show main menu\n'
        '/menu - Show main menu\n'
        '/status - System status\n'
        '/volume &lt;0-100&gt; - Set volume\n'
        '/copy &lt;text&gt; - Copy text\n'
        '/help - Show this help\n\n'
        '<b>Button Interface:</b>\n'
        'Use the interactive buttons for easier control!\n\n'
        '<b>File Operations:</b>\n'
        'Send any file to upload to PC\n'
        'Use Files menu to download',
        parse_mode=ParseMode.HTML
    )


@router.message(Command('status'))
async def cmd_status(message: Message):
    """Handle /status command"""
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


@router.message(Command('volume'))
async def cmd_volume(message: Message):
    """Handle /volume command"""
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
            reply_markup=keyboards.media_menu()
        )


@router.message(Command('copy'))
async def cmd_copy(message: Message):
    """Handle /copy command"""
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
            reply_markup=keyboards.clipboard_menu()
        )


@router.message(Command('battery'))
async def cmd_battery(message: Message):
    """Handle /battery command"""
    msg = await message.answer('🔋 Checking battery...')
    result = await client.send_command('battery_status')

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


@router.message(Command('network'))
async def cmd_network(message: Message):
    """Handle /network command"""
    msg = await message.answer('🌐 Getting network info...')
    result = await client.send_command('network_info')

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


@router.message(Command('processes'))
async def cmd_processes(message: Message):
    """Handle /processes command"""
    msg = await message.answer('💻 Getting process list...')
    result = await client.send_command('process_list', {'sort_by': 'cpu', 'limit': 10})

    if result.get('status') == 'success':
        text = result.get('details', result.get('message'))
    else:
        text = f"❌ {result.get('message')}"

    await msg.edit_text(text)


@router.message(Command('kill'))
async def cmd_kill(message: Message):
    """Handle /kill <pid> command"""
    try:
        args = message.text.split()
        if len(args) < 2:
            raise ValueError

        pid = int(args[1])

        msg = await message.answer(f'❌ Killing process {pid}...')
        result = await client.send_command('process_kill', {'pid': pid})

        icon = '✅' if result.get('status') == 'success' else '❌'
        await msg.edit_text(f"{icon} {result.get('message')}")

    except (IndexError, ValueError):
        await message.answer('❌ Usage: /kill <pid>\n\nExample: /kill 1234')


@router.message(Command('search'))
async def cmd_search(message: Message):
    """Handle /search <process_name> command"""
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            raise ValueError

        process_name = args[1].strip()

        msg = await message.answer(f'🔍 Searching for: {process_name}...')
        result = await client.send_command('process_search', {'name': process_name})

        if result.get('status') == 'success':
            text = result.get('details', result.get('message'))
        else:
            text = f"❌ {result.get('message')}"

        await msg.edit_text(text)

    except (IndexError, ValueError):
        await message.answer('❌ Usage: /search <process_name>\n\nExample: /search chrome')