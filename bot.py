import telebot
import os
import time
from flask import Flask

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # Telegram ID بتاعك
# ==========================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

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
        "📎 ابعت الملف وأنا هبعته فورًا لصاحب البوت"
    )

@bot.message_handler(content_types=["document"])
def receive_file(message):
    try:
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
        bot.reply_to(message, "❌ حصل خطأ")
        bot.send_message(ADMIN_ID, f"⚠️ Error:\n{e}")

# ================= RUN =================
def run_bot():
    print("🤖 Bot polling started")
    bot.remove_webhook(drop_pending_updates=True)
    bot.infinity_polling(
        timeout=30,
        long_polling_timeout=30,
        skip_pending=True
    )

if __name__ == "__main__":
    # شغّل البوت مرة واحدة فقط
    run_bot()

    # افتح بورت عشان Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
