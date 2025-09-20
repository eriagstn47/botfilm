import os
import asyncio
import logging
from dotenv import load_dotenv  # <-- Tambahan untuk tes lokal
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, ContextTypes)

# Panggil load_dotenv() di awal untuk memuat variabel dari file .env (untuk tes lokal)
load_dotenv()

# Mengaktifkan logging untuk debugging yang lebih baik
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# =================================================================
# === KONFIGURASI DIAMBIL DARI ENVIRONMENT VARIABLES ===
# =================================================================
# Mengambil semua konfigurasi dari lingkungan, bukan hardcode
TOKEN_UPDATE_BOT = os.environ.get("TOKEN_UPDATE_BOT")
CHAT_ID_GROUP_UPDATE = os.environ.get("CHAT_ID_GROUP_UPDATE")
TOKEN_REQUEST_BOT = os.environ.get("TOKEN_REQUEST_BOT")
ADMIN_CHAT_ID_REQUEST = os.environ.get("ADMIN_CHAT_ID_REQUEST")

# --- Validasi variabel ---
# Program akan berhenti jika salah satu variabel penting tidak ditemukan
if not all([TOKEN_UPDATE_BOT, CHAT_ID_GROUP_UPDATE, TOKEN_REQUEST_BOT, ADMIN_CHAT_ID_REQUEST]):
    raise ValueError("Pastikan semua environment variables (TOKEN_UPDATE_BOT, CHAT_ID_GROUP_UPDATE, TOKEN_REQUEST_BOT, ADMIN_CHAT_ID_REQUEST) sudah diatur!")

# Konversi Chat ID ke integer, karena environment variable selalu string
try:
    CHAT_ID_GROUP_UPDATE = int(CHAT_ID_GROUP_UPDATE)
    ADMIN_CHAT_ID_REQUEST = int(ADMIN_CHAT_ID_REQUEST)
except ValueError:
    raise ValueError("CHAT_ID_GROUP_UPDATE dan ADMIN_CHAT_ID_REQUEST harus berupa angka integer!")

# =================================================================
# === FUNGSI-FUNGSI UNTUK BOT 1 (UpdateFilmBot) ===
# =================================================================
# Tidak ada perubahan logika di sini
bot_update_sender = Bot(token=TOKEN_UPDATE_BOT)

def parse_input_update(text: str):
    data = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key.strip().lower()] = value.strip()
    return data

def format_template_update(data):
    return f"""🆕 **UPDATE FILM HARI INI** 🎬🔥

    ✨ Halo Sobat Movie Lovers! ✨

    Tiap hari kami bakal update film-film terbaru dan pilihan terbaik buat nemenin waktu santai kamu. 🍿

    🎥 **Judul Film Hari Ini**: {data.get('judul','-')}
    📅 **Tanggal Rilis**: {data.get('tanggal','-')}
    🎭 **Genre**: {data.get('genre','-')}
    ⭐ **Rating**: {data.get('rating','-')}
    🔍 **Source**: [{data.get('source_name', 'N/A')}]({data.get('source_url', '#')})

    🔗 **Tonton/Download Sekarang di sini**:
    {data.get('link','-')}

    🎉 Yuk jangan sampai ketinggalan! Follow terus update kami setiap hari supaya kamu jadi orang pertama yang tahu film-film keren terbaru.

    💬 *Share ke teman yang suka nonton juga biar sama-sama update.*"""

async def handle_update_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = parse_input_update(text)
    formatted_message = format_template_update(data)
    await bot_update_sender.send_message(chat_id=CHAT_ID_GROUP_UPDATE,
                                         text=formatted_message,
                                         parse_mode="Markdown")

# =================================================================
# === FUNGSI-FUNGSI UNTUK BOT 2 (RequestFilmBot) ===
# =================================================================
# Tidak ada perubahan logika di sini
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎬 Request Film"], ["🚨 Report Link Error"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    welcome_message = (
        "👋 Halo! Selamat datang di Bot Film.\n\n"
        "Tekan tombol di bawah untuk meminta film atau melaporkan link yang error."
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def request_film_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Silakan ketik: `/requestfilm [judul film]`", parse_mode="Markdown")

async def report_link_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Silakan ketik: `/report [judul film dan masalahnya]`", parse_mode="Markdown")

async def handle_request_film_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    request_text = " ".join(context.args)
    if not request_text:
        await request_film_prompt(update, context)
        return
    message_to_admin = f"📩 *REQUEST FILM BARU*\n\n👤 Dari: {username}\n🎬 Film: {request_text}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID_REQUEST, text=message_to_admin, parse_mode="Markdown")
    await update.message.reply_text("✅ Terima kasih, request film kamu sudah kami terima.")

async def handle_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    report_text = " ".join(context.args)
    if not report_text:
        await report_link_prompt(update, context)
        return
    message_to_admin = f"🚨 *LAPORAN LINK ERROR*\n\n👤 Dari: {username}\n💬 Laporan: {report_text}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID_REQUEST, text=message_to_admin, parse_mode="Markdown")
    await update.message.reply_text("✅ Terima kasih, laporan kamu sudah kami terima.")

async def unknown_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Maaf, saya tidak mengerti. Silakan gunakan tombol di bawah ini. 👇")

# =================================================================
# === BAGIAN MANAJER UTAMA (Asyncio) ===
# =================================================================
async def main():
    """Fungsi utama untuk membangun, mengkonfigurasi, dan menjalankan kedua bot."""
    logger.info("Memulai konfigurasi bot...")

    # --- Konfigurasi Bot 1 (UpdateFilmBot) ---
    app_update = ApplicationBuilder().token(TOKEN_UPDATE_BOT).build()
    app_update.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_message))

    # --- Konfigurasi Bot 2 (RequestFilmBot) ---
    app_request = ApplicationBuilder().token(TOKEN_REQUEST_BOT).build()
    app_request.add_handler(CommandHandler("start", start_handler))
    app_request.add_handler(CommandHandler("requestfilm", handle_request_film_command))
    app_request.add_handler(CommandHandler("report", handle_report_command))
    app_request.add_handler(MessageHandler(filters.Regex("^🎬 Request Film$"), request_film_prompt))
    app_request.add_handler(MessageHandler(filters.Regex("^🚨 Report Link Error$"), report_link_prompt))
    app_request.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text_handler))

    # Menjalankan kedua bot secara bersamaan
    async with app_update, app_request:
        logger.info("Menginisialisasi aplikasi...")
        await app_update.initialize()
        await app_request.initialize()

        logger.info("Memulai polling...")
        await app_update.updater.start_polling()
        await app_request.updater.start_polling()

        logger.info("Memulai aplikasi bot...")
        await app_update.start()
        await app_request.start()

        logger.info("✅ Kedua bot sekarang berjalan. Program akan tetap aktif.")
        # Loop tak terbatas untuk menjaga program tetap hidup
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot dihentikan.")
    except ValueError as e:
        logger.error(f"Error Konfigurasi: {e}")
