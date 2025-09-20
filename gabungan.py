import os
import asyncio  # Menggantikan threading
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, ContextTypes)
from stay_alive import keep_alive

# from keep_alive import keep_alive # Jika pakai Replit

# =================================================================
# === KONFIGURASI (SAMA SEPERTI SEBELUMNYA) ===
# =================================================================
TOKEN_UPDATE_BOT = "7529671551:AAE2vdshvR9W-v-J8td13QEsNQXOZS0w6og"
CHAT_ID_GROUP_UPDATE = -1002948360397
TOKEN_REQUEST_BOT = "8238885907:AAH34IzIThJ2y-VWbYncxGBZjrl6dwVrHRo"
ADMIN_CHAT_ID_REQUEST = -1002974809284

# =================================================================
# === FUNGSI-FUNGSI UNTUK BOT 1 (UpdateFilmBot) ===
# =================================================================
# Tidak ada perubahan di bagian ini, semua fungsi sama
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


async def handle_update_message(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = parse_input_update(text)
    formatted_message = format_template_update(data)
    await bot_update_sender.send_message(chat_id=CHAT_ID_GROUP_UPDATE,
                                         text=formatted_message,
                                         parse_mode="Markdown")


# =================================================================
# === FUNGSI-FUNGSI UNTUK BOT 2 (RequestFilmBot) ===
# =================================================================
# Tidak ada perubahan di bagian ini, semua handler sama
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎬 Request Film"], ["🚨 Report Link Error"]]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=False)
    welcome_message = (
        "👋 Halo! Selamat datang di Bot Film.\n\n"
        "Tekan tombol di bawah untuk meminta film atau melaporkan link yang error."
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def request_film_prompt(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Silakan ketik: `/requestfilm [judul film]`", parse_mode="Markdown")


async def report_link_prompt(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Silakan ketik: `/report [judul film dan masalahnya]`",
        parse_mode="Markdown")


async def handle_request_film_command(update: Update,
                                      context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    request_text = " ".join(context.args)
    if not request_text:
        await request_film_prompt(update, context)
        return
    message_to_admin = f"📩 *REQUEST FILM BARU*\n\n👤 Dari: {username}\n🎬 Film: {request_text}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID_REQUEST,
                                   text=message_to_admin,
                                   parse_mode="Markdown")
    await update.message.reply_text(
        "✅ Terima kasih, request film kamu sudah kami terima.")


async def handle_report_command(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    report_text = " ".join(context.args)
    if not report_text:
        await report_link_prompt(update, context)
        return
    message_to_admin = f"🚨 *LAPORAN LINK ERROR*\n\n👤 Dari: {username}\n💬 Laporan: {report_text}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID_REQUEST,
                                   text=message_to_admin,
                                   parse_mode="Markdown")
    await update.message.reply_text(
        "✅ Terima kasih, laporan kamu sudah kami terima.")


async def unknown_text_handler(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Maaf, saya tidak mengerti. Silakan gunakan tombol di bawah ini. 👇")


## =================================================================
# === BAGIAN MANAJER BARU (Menggunakan Asyncio) - VERSI PERBAIKAN ===
# =================================================================
async def main():
    """Fungsi utama untuk membangun, mengkonfigurasi, dan menjalankan kedua bot."""

    # --- Konfigurasi Bot 1 (UpdateFilmBot) ---
    app_update = ApplicationBuilder().token(TOKEN_UPDATE_BOT).build()
    app_update.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_message))

    # --- Konfigurasi Bot 2 (RequestFilmBot) ---
    app_request = ApplicationBuilder().token(TOKEN_REQUEST_BOT).build()
    app_request.add_handler(CommandHandler("start", start_handler))
    app_request.add_handler(
        CommandHandler("requestfilm", handle_request_film_command))
    app_request.add_handler(CommandHandler("report", handle_report_command))
    app_request.add_handler(
        MessageHandler(filters.Regex("^🎬 Request Film$"), request_film_prompt))
    app_request.add_handler(
        MessageHandler(filters.Regex("^🚨 Report Link Error$"),
                       report_link_prompt))
    app_request.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text_handler))

    # LANGKAH 1: Inisialisasi kedua bot terlebih dahulu.
    # Kita tunggu sampai langkah ini benar-benar selesai.
    print("Menginisialisasi aplikasi...")
    await app_update.initialize()
    await app_request.initialize()

    # LANGKAH 2: Mulai polling untuk kedua bot.
    # Perintah ini tidak blocking, jadi akan langsung lanjut ke langkah berikutnya.
    print("Memulai polling...")
    await app_update.updater.start_polling()
    await app_request.updater.start_polling()

    # LANGKAH 3: Mulai aplikasi bot untuk memproses update.
    # Perintah ini juga tidak blocking.
    print("Memulai aplikasi bot...")
    await app_update.start()
    await app_request.start()

    # LANGKAH 4: Jaga agar program tetap berjalan.
    print("✅ Kedua bot sekarang berjalan. Tekan Ctrl-C untuk berhenti.")
    while True:
        await asyncio.sleep(
            3600
        )  # Program akan diam di sini dan bot tetap aktif di background


if __name__ == "__main__":
    # keep_alive() # Aktifkan jika di Replit

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot dihentikan.")
    except RuntimeError as e:
        print(f"Terjadi error saat menjalankan bot: {e}")
