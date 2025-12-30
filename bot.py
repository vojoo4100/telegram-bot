import telebot
import os
from flask import Flask
from threading import Thread

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # عدل لو لزم
# =========================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# نخزن الربط بين رسالة الأدمن والمستخدم
reply_map = {}

# ================= FLASK (Render) =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

# ================= USER SIDE =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 أهلاً بيك\n"
        "📎 ابعت الملف وهيوصل للأدمن فورًا"
    )

@bot.message_handler(content_types=["document"])
def receive_file(message):
    try:
        sent = bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=(
                "📁 <b>ملف جديد</b>\n"
                f"👤 من: @{message.from_user.username}\n"
                f"🆔 ID: {message.from_user.id}\n\n"
                "✏️ <b>اعمل Reply على الرسالة دي علشان تبعت الرد لنفس الشخص</b>"
            )
        )

        # نربط رسالة الأدمن بالمستخدم
        reply_map[sent.message_id] = message.from_user.id

        bot.reply_to(message, "✅ الملف وصل للأدمن")

    except Exception as e:
        bot.reply_to(message, "❌ حصل خطأ أثناء الإرسال")
        bot.send_message(ADMIN_ID, f"⚠️ Error:\n{e}")

# ================= ADMIN SIDE =================
@bot.message_handler(func=lambda m: m.reply_to_message is not None)
def admin_reply(message):
    # تأكيد إن اللي بيرد هو الأدمن
    if message.from_user.id != ADMIN_ID:
        return

    replied_id = message.reply_to_message.message_id

    if replied_id not in reply_map:
        bot.reply_to(message, "❌ الرد ده مش مربوط بأي مستخدم")
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

        # نحذف الربط بعد الإرسال
        del reply_map[replied_id]

    except Exception as e:
        bot.reply_to(message, f"❌ خطأ:\n{e}")

# ================= RUN =================
def run_bot():
    print("🤖 Bot polling started")

    # مهم جدًا: نمسح أي webhook قديم
    bot.delete_webhook(drop_pending_updates=True)

    bot.infinity_polling(
        timeout=30,
        long_polling_timeout=30
    )

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_flask()
