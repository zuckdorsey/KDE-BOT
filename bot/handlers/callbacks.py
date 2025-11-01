"""
Callback query handlers for inline buttons
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.enums import ParseMode

import keyboards
from client import SystemClient

router = Router()
client = SystemClient()


# ===========================
# MENU NAVIGATION
# ===========================

@router.callback_query(F.data == 'menu_main')
async def callback_menu_main(callback: CallbackQuery):
    """Show main menu"""
    await callback.message.edit_text(
        '📱 <b>Main Menu</b>\n\nSelect an option:',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == 'menu_system')
async def callback_menu_system(callback: CallbackQuery):
    """Show system menu"""
    await callback.message.edit_text(
        '🖥️ <b>System Control</b>\n\nChoose an action:',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.system_menu()
    )
    await callback.answer()


@router.callback_query(F.data == 'menu_media')
async def callback_menu_media(callback: CallbackQuery):
    """Show media menu"""
    await callback.message.edit_text(
        '🔊 <b>Media Control</b>\n\nAdjust volume or mute:',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.media_menu()
    )
    await callback.answer()


@router.callback_query(F.data == 'menu_clipboard')
async def callback_menu_clipboard(callback: CallbackQuery):
    """Show clipboard menu"""
    await callback.message.edit_text(
        '📋 <b>Clipboard Manager</b>\n\nManage clipboard:',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.clipboard_menu()
    )
    await callback.answer()


@router.callback_query(F.data == 'menu_files')
async def callback_menu_files(callback: CallbackQuery):
    """Show files menu"""
    await callback.message.edit_text(
        '📁 <b>File Manager</b>\n\nFile operations:',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.files_menu()
    )
    await callback.answer()


# ===========================
# SYSTEM COMMANDS
# ===========================

@router.callback_query(F.data == 'cmd_lock')
async def callback_cmd_lock(callback: CallbackQuery):
    """Lock screen"""
    await callback.answer('🔒 Locking screen...')

    result = await client.send_command('lock')
    icon = '✅' if result.get('status') == 'success' else '❌'

    await callback.message.edit_text(
        f"{icon} {result.get('message')}",
        reply_markup=keyboards.system_menu()
    )


@router.callback_query(F.data == 'cmd_sleep')
async def callback_cmd_sleep(callback: CallbackQuery):
    """Put PC to sleep"""
    await callback.answer('😴 Putting PC to sleep...')

    result = await client.send_command('sleep')
    icon = '✅' if result.get('status') == 'success' else '❌'

    await callback.message.edit_text(
        f"{icon} {result.get('message')}",
        reply_markup=keyboards.system_menu()
    )


@router.callback_query(F.data == 'cmd_screenshot')
async def callback_cmd_screenshot(callback: CallbackQuery):
    """Take screenshot"""
    await callback.answer('📸 Taking screenshot...')

    try:
        result = await client.send_command('screenshot')

        if result.get('status') == 'success' and result.get('file'):
            # Download screenshot
            screenshot_data = await client.get_screenshot(result['file'])

            # Send as photo
            photo = BufferedInputFile(screenshot_data, filename='screenshot.png')
            await callback.message.answer_photo(
                photo=photo,
                caption='📸 Screenshot',
                reply_markup=keyboards.system_menu()
            )
            await callback.message.delete()
        else:
            await callback.message.edit_text(
                f"❌ {result.get('message')}",
                reply_markup=keyboards.system_menu()
            )
    except Exception as e:
        await callback.message.edit_text(
            f'❌ Error: {str(e)}',
            reply_markup=keyboards.system_menu()
        )


@router.callback_query(F.data == 'cmd_shutdown_warn')
async def callback_cmd_shutdown_warn(callback: CallbackQuery):
    """Show shutdown warning"""
    await callback.message.edit_text(
        '⚠️ <b>SHUTDOWN WARNING</b>\n\n'
        'Are you sure you want to shutdown your PC?\n\n'
        'This action cannot be undone!',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.shutdown_confirm()
    )
    await callback.answer()


@router.callback_query(F.data == 'cmd_shutdown')
async def callback_cmd_shutdown(callback: CallbackQuery):
    """Shutdown PC"""
    await callback.answer('⚠️ Shutting down...')

    result = await client.send_command('shutdown')
    icon = '✅' if result.get('status') == 'success' else '❌'

    await callback.message.edit_text(f"{icon} {result.get('message')}")


# ===========================
# MEDIA COMMANDS
# ===========================

@router.callback_query(F.data == 'cmd_mute')
async def callback_cmd_mute(callback: CallbackQuery):
    """Toggle mute"""
    await callback.answer('🔇 Toggling mute...')

    result = await client.send_command('mute')
    icon = '✅' if result.get('status') == 'success' else '❌'

    await callback.message.edit_text(
        f"{icon} {result.get('message')}",
        reply_markup=keyboards.media_menu()
    )


@router.callback_query(F.data.startswith('cmd_vol_'))
async def callback_cmd_volume(callback: CallbackQuery):
    """Set volume"""
    level = int(callback.data.split('_')[-1])
    await callback.answer(f'🔊 Setting volume to {level}%...')

    result = await client.send_command('volume', {'level': level})
    icon = '✅' if result.get('status') == 'success' else '❌'

    await callback.message.edit_text(
        f"{icon} {result.get('message')}",
        reply_markup=keyboards.media_menu()
    )


# ===========================
# CLIPBOARD COMMANDS
# ===========================

@router.callback_query(F.data == 'cmd_paste')
async def callback_cmd_paste(callback: CallbackQuery):
    """Get clipboard content"""
    await callback.answer('📋 Getting clipboard...')

    try:
        result = await client.send_command('paste')
        content = result.get('content', '(empty)')

        await callback.message.edit_text(
            f"📋 <b>Clipboard Content:</b>\n\n<code>{content}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.clipboard_menu()
        )
    except Exception as e:
        await callback.message.edit_text(
            f'❌ Error: {str(e)}',
            reply_markup=keyboards.clipboard_menu()
        )


@router.callback_query(F.data == 'cmd_copy_prompt')
async def callback_cmd_copy_prompt(callback: CallbackQuery):
    """Show copy prompt"""
    await callback.message.reply(
        '✍️ <b>Copy Text to Clipboard</b>\n\n'
        'Send me the text you want to copy:\n\n'
        'Example: <code>Hello World</code>\n'
        'Or use: <code>/copy your text here</code>',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.clipboard_menu()
    )
    await callback.answer()


# ===========================
# FILE COMMANDS
# ===========================

@router.callback_query(F.data == 'cmd_upload_prompt')
async def callback_cmd_upload_prompt(callback: CallbackQuery):
    """Show upload prompt"""
    await callback.message.reply(
        '📤 <b>Upload File to PC</b>\n\n'
        'Send me any file (document, image, video, etc.) '
        'and I will save it to your PC.',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.files_menu()
    )
    await callback.answer()


@router.callback_query(F.data == 'cmd_download_prompt')
async def callback_cmd_download_prompt(callback: CallbackQuery):
    """Show download prompt"""
    await callback.message.reply(
        '📥 <b>Download File from PC</b>\n\n'
        'Send the full file path:\n\n'
        'Example:\n'
        '<code>/home/user/document.pdf</code>\n'
        '<code>C:\\Users\\user\\file.txt</code>',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.files_menu()
    )
    await callback.answer()


# ===========================
# STATUS
# ===========================

@router.callback_query(F.data == 'cmd_status')
async def callback_cmd_status(callback: CallbackQuery):
    """Get system status"""
    await callback.answer('🔍 Checking system...')

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

        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.main_menu()
        )
    except Exception as e:
        await callback.message.edit_text(
            f'❌ Error: {str(e)}',
            reply_markup=keyboards.main_menu()
        )

    @router.callback_query(F.data == 'menu_player')
    async def callback_menu_player(callback: CallbackQuery):
        """Show media player menu"""
        await callback.message.edit_text(
            '🎵 <b>Media Player Control</b>\n\nControl your media playback:',
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.player_menu()
        )
        await callback.answer()

    @router.callback_query(F.data == 'menu_network')
    async def callback_menu_network(callback: CallbackQuery):
        """Show network menu"""
        await callback.message.edit_text(
            '🌐 <b>Network Information</b>\n\nView network details:',
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.network_menu()
        )
        await callback.answer()

    @router.callback_query(F.data == 'menu_processes')
    async def callback_menu_processes(callback: CallbackQuery):
        """Show processes menu"""
        await callback.message.edit_text(
            '💻 <b>Process Manager</b>\n\nManage running processes:',
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.processes_menu()
        )
        await callback.answer()

    # Media player handlers
    @router.callback_query(F.data == 'media_play_pause')
    async def callback_media_play_pause(callback: CallbackQuery):
        await callback.answer('⏯️ Toggling play/pause...')
        result = await client.send_command('media_play_pause')
        icon = '✅' if result.get('status') == 'success' else '❌'
        await callback.message.edit_text(
            f"{icon} {result.get('message')}",
            reply_markup=keyboards.player_menu()
        )

    @router.callback_query(F.data == 'media_next')
    async def callback_media_next(callback: CallbackQuery):
        await callback.answer('⏭️ Next track...')
        result = await client.send_command('media_next')
        icon = '✅' if result.get('status') == 'success' else '❌'
        await callback.message.edit_text(
            f"{icon} {result.get('message')}",
            reply_markup=keyboards.player_menu()
        )

    @router.callback_query(F.data == 'media_previous')
    async def callback_media_previous(callback: CallbackQuery):
        await callback.answer('⏮️ Previous track...')
        result = await client.send_command('media_previous')
        icon = '✅' if result.get('status') == 'success' else '❌'
        await callback.message.edit_text(
            f"{icon} {result.get('message')}",
            reply_markup=keyboards.player_menu()
        )

    @router.callback_query(F.data == 'media_stop')
    async def callback_media_stop(callback: CallbackQuery):
        await callback.answer('⏹️ Stopping...')
        result = await client.send_command('media_stop')
        icon = '✅' if result.get('status') == 'success' else '❌'
        await callback.message.edit_text(
            f"{icon} {result.get('message')}",
            reply_markup=keyboards.player_menu()
        )

    @router.callback_query(F.data == 'media_now_playing')
    async def callback_media_now_playing(callback: CallbackQuery):
        await callback.answer('🎵 Getting track info...')
        result = await client.send_command('media_now_playing')

        if result.get('status') == 'success':
            track = result.get('track', 'No track playing')
            playback = result.get('playback_status', '')

            text = f"🎵 <b>Now Playing</b>\n\n{track}"
            if playback:
                text += f"\n📊 Status: {playback}"
        else:
            text = f"❌ {result.get('message')}"

        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.player_menu()
        )

    # Battery handler
    @router.callback_query(F.data == 'cmd_battery')
    async def callback_cmd_battery(callback: CallbackQuery):
        await callback.answer('🔋 Checking battery...')
        result = await client.send_command('battery_status')

        if result.get('status') == 'success':
            text = result.get('details', result.get('message'))
        else:
            text = f"❌ {result.get('message')}"

        await callback.message.edit_text(
            text,
            reply_markup=keyboards.main_menu()
        )

    # Network handlers
    @router.callback_query(F.data == 'cmd_network_info')
    async def callback_cmd_network_info(callback: CallbackQuery):
        await callback.answer('🌐 Getting network info...')
        result = await client.send_command('network_info')

        if result.get('status') == 'success':
            text = result.get('details', result.get('message'))
        else:
            text = f"❌ {result.get('message')}"

        await callback.message.edit_text(
            text,
            reply_markup=keyboards.network_menu()
        )

    @router.callback_query(F.data == 'cmd_network_stats')
    async def callback_cmd_network_stats(callback: CallbackQuery):
        await callback.answer('📊 Getting network stats...')
        result = await client.send_command('network_stats')

        if result.get('status') == 'success':
            text = result.get('details', result.get('message'))
        else:
            text = f"❌ {result.get('message')}"

        await callback.message.edit_text(
            text,
            reply_markup=keyboards.network_menu()
        )

    # Process handlers
    @router.callback_query(F.data == 'proc_list_cpu')
    async def callback_proc_list_cpu(callback: CallbackQuery):
        await callback.answer('📊 Getting top CPU processes...')
        result = await client.send_command('process_list', {'sort_by': 'cpu', 'limit': 10})

        if result.get('status') == 'success':
            text = result.get('details', result.get('message'))
        else:
            text = f"❌ {result.get('message')}"

        await callback.message.edit_text(
            text,
            reply_markup=keyboards.processes_menu()
        )

    @router.callback_query(F.data == 'proc_list_mem')
    async def callback_proc_list_mem(callback: CallbackQuery):
        await callback.answer('💾 Getting top RAM processes...')
        result = await client.send_command('process_list', {'sort_by': 'memory', 'limit': 10})

        if result.get('status') == 'success':
            text = result.get('details', result.get('message'))
        else:
            text = f"❌ {result.get('message')}"

        await callback.message.edit_text(
            text,
            reply_markup=keyboards.processes_menu()
        )

    @router.callback_query(F.data == 'proc_search_prompt')
    async def callback_proc_search_prompt(callback: CallbackQuery):
        await callback.message.reply(
            '🔍 <b>Search Process</b>\n\n'
            'Send the process name to search:\n\n'
            'Example: <code>chrome</code> or <code>firefox</code>',
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.processes_menu()
        )
        await callback.answer()

    @router.callback_query(F.data == 'proc_kill_prompt')
    async def callback_proc_kill_prompt(callback: CallbackQuery):
        await callback.message.reply(
            '❌ <b>Kill Process</b>\n\n'
            'Send the PID (Process ID) to kill:\n\n'
            'Example: <code>/kill 1234</code>\n\n'
            '⚠️ Warning: This will terminate the process!',
            parse_mode=ParseMode.HTML,
            reply_markup=keyboards.processes_menu()
        )
        await callback.answer()