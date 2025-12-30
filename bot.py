import telebot
import os
from flask import Flask
from threading import Thread

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733
# =========================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN)

# ربط رسالة الأدمن باليوزر
reply_map = {}

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

# ================= USER SIDE =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "📎 ابعت الملف الكونفج المراد فكه\n"
        "⏳ برجاء الانتظار بعد الإرسال"
    )

@bot.message_handler(content_types=["document"])
def receive_file(message):
    sent = bot.send_document(
        ADMIN_ID,
        message.document.file_id,
        caption=(
            "📁 ملف جديد\n"
            f"👤 من: @{message.from_user.username}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            "✏️ اعمل Reply هنا علشان تبعت الرد لنفس الشخص"
        )
    )

    reply_map[sent.message_id] = message.from_user.id

    bot.reply_to(
        message,
        "✅ تم الاستلام\n"
        "⏱️ انتظر بصبر من ساعة لـ ساعتين\n"
        "وسيتم فك الملف وإرجاعه لك"
    )

# ================= ADMIN SIDE =================
@bot.message_handler(func=lambda m: m.reply_to_message is not None)
def admin_reply(message):
    replied_id = message.reply_to_message.message_id

    if replied_id not in reply_map:
        return

    user_id = reply_map[replied_id]

    try:
        if message.content_type == "text":
            bot.send_message(user_id, message.text)

        elif message.content_type == "document":
            bot.send_document(user_id, message.document.file_id)

        elif message.content_type == "photo":
            bot.send_photo(user_id, message.photo[-1].file_id)

        bot.reply_to(message, "✅ تم الإرسال للمستخدم")

    except Exception as e:
        bot.reply_to(message, f"❌ خطأ:\n{e}")

# ================= RUN =================
def run_bot():
    bot.infinity_polling(skip_pending=True)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_flask()
