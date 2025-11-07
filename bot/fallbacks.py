"""
Fallback handlers to catch unknown commands/text and old inline callbacks.
"""

import logging
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
import config

logger = logging.getLogger(__name__)


def _authorized(msg_user_id: int) -> bool:
    return msg_user_id == config.OWNER_ID


async def unknown_command(message: Message):
    """
    Catch-all untuk command tak dikenal (mulai dengan '/').
    Letakkan handler ini PALING AKHIR setelah semua command valid.
    """
    if not _authorized(message.from_user.id):
        return
    text = (
        "❓ Perintah tidak dikenal.\n"
        "Ketik /help untuk daftar perintah atau tekan tombol di keyboard di bawah.\n\n"
        "Tips: gunakan tombol, bukan mengetik manual agar teks persis sama."
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


async def unknown_text(message: Message):
    """
    Catch-all untuk teks biasa yang tidak cocok filter mana pun.
    Letakkan PALING AKHIR sesudah semua handler F.text lainnya.
    """
    # Jika bukan owner, diam (auth layer Anda sudah menangani unauthorized)
    if not _authorized(message.from_user.id):
        return

    # Bisa log teks yang tidak dikenali untuk debugging
    t = message.text or ''
    logger.info("Unknown text from %s: %r", message.from_user.id, t)

    await message.answer(
        "🤖 Aku tidak paham pesanmu.\n"
        "Silakan gunakan tombol keyboard atau ketik /help.",
        parse_mode=ParseMode.HTML
    )


async def fallback_callback(callback: CallbackQuery):
    """
    Catch-all untuk semua callback_query (inline button lama).
    Versi ini pakai Reply Keyboard, jadi arahkan user kembali ke /start.
    """
    try:
        if callback.from_user.id != config.OWNER_ID:
            await callback.answer('❌ Unauthorized', show_alert=True)
            return

        # Jawab callback biar tidak "loading" di klien
        await callback.answer("UI terbaru menggunakan keyboard tetap. Kirim /start untuk membuka menu.", show_alert=True)

        # Opsional kirim pesan instruksi
        await callback.message.answer(
            "ℹ️ UI telah berpindah ke Reply Keyboard (tombol di bawah kolom chat).\n"
            "Kirim /start untuk membuka menu utama.",
            parse_mode=ParseMode.HTML
        )
    except Exception:
        # Jangan sampai error callback bikin loop
        pass