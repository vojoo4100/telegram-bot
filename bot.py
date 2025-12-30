import telebot
import os
from flask import Flask
from threading import Thread

# ============== CONFIG ==============
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733   # ايدي الأدمن
# ====================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# نخزن: message_id (رسالة الأدمن) -> user_id
reply_map = {}

# ============== FLASK (عشان Render) ==============
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

# ============== USER SIDE ==============
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 أهلاً بيك\n"
        "📎 ابعت الملف الكونفج المراد فكة ✅"
    )

@bot.message_handler(content_types=["document"])
def receive_file(message):
    sent = bot.send_document(
        ADMIN_ID,
        message.document.file_id,
        caption=(
            "📁 <b>ملف جديد</b>\n"
            f"📄 الاسم: <code>{message.document.file_name}</code>\n"
            f"👤 من: @{message.from_user.username}\n"
            f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
            "✏️ اعمل Reply هنا علشان تبعت الرد لنفس الشخص"
        )
    )

    # نربط رسالة الأدمن بالمستخدم
    reply_map[sent.message_id] = message.from_user.id

    bot.reply_to(
        message,
        "✅ تم الاستلام\n"
        "⏳ انتظر بصبر من ساعة لـ ساعتين وهيتم فك الملف\n"
        "📤 واسترجاعلك الملف المفكوك"
    )

# ============== ADMIN SIDE ==============
@bot.message_handler(func=lambda m: m.reply_to_message is not None)
def admin_reply(message):
    # الأدمن بس
    if message.from_user.id != ADMIN_ID:
        return

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

        # نحذف الربط بعد الإرسال
        del reply_map[replied_id]

    except Exception as e:
        bot.reply_to(message, f"❌ خطأ:\n{e}")

# ============== RUN ==============
def run_bot():
    print("🤖 Bot started")
    bot.delete_webhook(drop_pending_updates=True)
    bot.infinity_polling(skip_pending=True)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_flask()
