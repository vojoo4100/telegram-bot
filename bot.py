import telebot
import os
import time

# ====== الإعدادات ======
TOKEN = os.environ.get("BOT_TOKEN")  # التوكن من Render Environment
ADMIN_ID = 5778768733  # ✏️ غيره لو حابب (ID بتاعك)

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

# ====== أوامر ======
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 أهلاً بيك\n"
        "📎 ابعت الملف اللي عايز توصله للإدمن"
    )

# ====== استقبال الملفات ======
@bot.message_handler(content_types=["document"])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_name = message.document.file_name
        file_path = os.path.join(FILES_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(downloaded_file)

        # تأكيد للمرسل
        bot.reply_to(message, f"✅ تم استلام الملف: {file_name}")

        # إرسال الملف للإدمن
        with open(file_path, "rb") as f:
            bot.send_document(
                ADMIN_ID,
                f,
                caption=(
                    "📥 ملف جديد وصل\n\n"
                    f"👤 من: {message.from_user.first_name}\n"
                    f"🆔 ID: {message.from_user.id}\n"
                    f"📄 اسم الملف: {file_name}"
                )
            )

    except Exception as e:
        bot.reply_to(message, "❌ حصل خطأ أثناء استلام الملف")
        bot.send_message(ADMIN_ID, f"⚠️ Error:\n{e}")

# ====== تشغيل البوت ======
def run_bot():
    print("🤖 Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("❌ Error, restarting bot:", e)
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
