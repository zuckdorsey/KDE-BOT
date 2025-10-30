"""
File upload/download handlers
"""

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.enums import ParseMode
import os

import keyboards
from client import SystemClient

router = Router()
client = SystemClient()


@router.message(F.document)
async def handle_document(message: Message):
    """Handle document upload"""
    msg = await message.answer('📥 Uploading file to PC...')

    try:
        file = await message.bot.get_file(message.document.file_id)
        file_url = message.bot.session.api.file_url(message.bot.token, file.file_path)

        result = await client.upload_file(
            filename=message.document.file_name,
            file_url=file_url,
            file_size=message.document.file_size
        )

        if result.get('status') == 'success':
            await msg.edit_text(
                f"✅ <b>File Uploaded</b>\n\n📁 <code>{result.get('path')}</code>",
                parse_mode=ParseMode.HTML,
                reply_markup=keyboards.main_menu()
            )
        else:
            await msg.edit_text(
                f"❌ {result.get('message')}",
                reply_markup=keyboards.main_menu()
            )
    except Exception as e:
        await msg.edit_text(
            f'❌ Error: {str(e)}',
            reply_markup=keyboards.main_menu()
        )


@router.message(F.photo)
async def handle_photo(message: Message):
    """Handle photo upload"""
    msg = await message.answer('📸 Saving photo to PC...')

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_url = message.bot.session.api.file_url(message.bot.token, file.file_path)

        filename = f'photo_{int(message.date.timestamp())}.jpg'

        result = await client.upload_file(
            filename=filename,
            file_url=file_url,
            file_size=photo.file_size
        )

        if result.get('status') == 'success':
            await msg.edit_text(
                f"✅ <b>Photo Saved</b>\n\n📁 <code>{result.get('path')}</code>",
                parse_mode=ParseMode.HTML,
                reply_markup=keyboards.main_menu()
            )
        else:
            await msg.edit_text(
                f"❌ {result.get('message')}",
                reply_markup=keyboards.main_menu()
            )
    except Exception as e:
        await msg.edit_text(
            f'❌ Error: {str(e)}',
            reply_markup=keyboards.main_menu()
        )


@router.message(F.text & ~F.text.startswith('/'))
async def handle_text(message: Message):
    """Handle text messages (for file path or copy)"""
    text = message.text

    # Check if it looks like a file path
    if '/' in text or '\\' in text:
        msg = await message.answer('📥 Retrieving file from PC...')

        try:
            file_data = await client.download_file(text)
            filename = os.path.basename(text)

            # Send as document
            document = BufferedInputFile(file_data, filename=filename)
            await message.answer_document(
                document=document,
                reply_markup=keyboards.files_menu()
            )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(
                f'❌ Error: {str(e)}',
                reply_markup=keyboards.files_menu()
            )
    else:
        # Assume it's text to copy
        msg = await message.answer('⏳ Copying to clipboard...')
        result = await client.send_command('copy', {'text': text})

        icon = '✅' if result.get('status') == 'success' else '❌'
        await msg.edit_text(f"{icon} {result.get('message')}")