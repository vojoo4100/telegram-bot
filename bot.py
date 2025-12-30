import telebot
import os
import time
from flask import Flask

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # ✏️ Telegram ID بتاعك
# ==========================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# تخزين مؤقت: اسم الملف -> user_id
file_owners = {}

# ================= FLASK (عشان Render) =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

# ================= TELEGRAM =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 أهلاً بيك\n"
        "📎 ابعت الملف وهيتبعت فورًا للإدمن\n"
        "📤 وهيرجعلك بعد التعديل"
    )

# ===== استقبال ملف من أي مستخدم =====
@bot.message_handler(content_types=["document"])
def receive_file(message):
    try:
        file_name = message.document.file_name
        user_id = message.from_user.id

        # حفظ صاحب الملف
        file_owners[file_name] = user_id

        # إرسال الملف للإدمن
        bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=(
                "📁 <b>ملف جديد</b>\n\n"
                f"📄 الاسم: {file_name}\n"
                f"👤 من: @{message.from_user.username}\n"
                f"🆔 ID: {user_id}\n\n"
                "✏️ بعد التعديل ابعته بنفس الاسم"
            )
        )

        bot.reply_to(message, "✅ تم إرسال الملف للإدمن")

    except Exception as e:
        bot.reply_to(message, "❌ حصل خطأ")
        bot.send_message(ADMIN_ID, f"⚠️ Error:\n{e}")

# ===== استقبال ملف من الأدمن =====
@bot.message_handler(content_types=["document"])
def receive_from_admin(message):
    if message.from_user.id != ADMIN_ID:
        return

    file_name = message.document.file_name

    if file_name not in file_owners:
        bot.reply_to(message, "❌ الملف ده مش معروف")
        return

    user_id = file_owners[file_name]

    try:
        bot.send_document(
            user_id,
            message.document.file_id,
            caption="✅ تم تعديل ملفك وإرجاعه"
        )

        bot.reply_to(message, "📤 تم إرسال الملف لصاحبه")

        # مسح بعد الإرسال
        del file_owners[file_name]

    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Error:\n{e}")

# ================= RUN =================
def run_bot():
    print("🤖 Bot polling started")
    bot.infinity_polling(timeout=30, long_polling_timeout=30)

if __name__ == "__main__":
    # تشغيل البوت في Thread
    import threading
    threading.Thread(target=run_bot).start()

    # فتح بورت لـ Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
