import telebot
import os
import time

# ================== الإعدادات ==================
TOKEN = os.environ.get("BOT_TOKEN")  # التوكن من Render
ADMIN_ID = 5778768733  # ❗ غيره لرقم Telegram ID بتاعك
FILES_DIR = "files"

# ==============================================

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN مش موجود في Environment Variables")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

os.makedirs(FILES_DIR, exist_ok=True)


# ========== /start ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "👋 أهلاً بيك\n\n"
        "📤 ابعتلي ملف وأنا هبعته فورًا لصاحب البوت"
    )


# ========== استقبال الملفات ==========
@bot.message_handler(content_types=['document'])
def receive_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        file_name = message.document.file_name
        file_path = os.path.join(FILES_DIR, file_name)

        with open(file_path, 'wb') as f:
            f.write(downloaded)

        # ابعت الملف للأدمن
        bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=(
                "📁 <b>ملف جديد</b>\n"
                f"👤 من: @{message.from_user.username}\n"
                f"🆔 ID: {message.from_user.id}"
            )
        )

        bot.reply_to(message, "✅ تم إرسال الملف بنجاح")

    except Exception as e:
        bot.reply_to(message, "❌ حصل خطأ أثناء إرسال الملف")
        bot.send_message(ADMIN_ID, f"⚠️ خطأ:\n{e}")


# ========== أي رسالة تانية ==========
@bot.message_handler(func=lambda m: True)
def other(message):
    bot.reply_to(message, "📎 من فضلك ابعت ملف فقط")


# ========== تشغيل البوت ==========
print("🤖 Bot is running...")
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(5)
