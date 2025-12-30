import telebot
import os
from flask import Flask
import threading

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733   # غيره لو حابب
# =========================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# نحفظ اليوزر اللي الأدمن هيبعتله
current_target = {}

# ================= FLASK (Render يحتاج بورت) =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= TELEGRAM =================

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🔥 أهلاً بيك\n"
        "📎 ابعت الملف وأنا هبعته لصاحب البوت"
    )

# المستخدم يبعت ملف
@bot.message_handler(content_types=["document"])
def receive_file(message):
    try:
        bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=(
                "📁 <b>ملف جديد</b>\n"
                f"📄 الاسم: <code>{message.document.file_name}</code>\n"
                f"👤 من: @{message.from_user.username}\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
                "✏️ بعد التعديل ابعته بنفس الاسم"
            )
        )
        bot.reply_to(message, "✅ الملف وصل، انتظر المعالجة")
    except Exception as e:
        bot.reply_to(message, "❌ حصل خطأ")
        bot.send_message(ADMIN_ID, f"⚠️ Error:\n{e}")

# الأدمن يحدد اليوزر
@bot.message_handler(commands=["send"])
def set_target(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "❌ استخدم:\n/send USER_ID")
        return

    try:
        user_id = int(parts[1])
    except:
        bot.reply_to(message, "❌ ID غير صحيح")
        return

    current_target[ADMIN_ID] = user_id
    bot.reply_to(
        message,
        f"✅ جاهز للإرسال إلى:\n<code>{user_id}</code>\n\n"
        "📤 ابعت الملف أو الرسالة دلوقتي"
    )

# الأدمن يبعت الملف أو الرسالة
@bot.message_handler(
    func=lambda m: m.from_user.id == ADMIN_ID and ADMIN_ID in current_target,
    content_types=["text", "document", "photo"]
)
def send_to_user(message):
    user_id = current_target[ADMIN_ID]

    try:
        if message.content_type == "text":
            bot.send_message(user_id, message.text)

        elif message.content_type == "document":
            bot.send_document(user_id, message.document.file_id)

        elif message.content_type == "photo":
            bot.send_photo(user_id, message.photo[-1].file_id)

        bot.reply_to(message, "✅ تم الإرسال بنجاح")
        del current_target[ADMIN_ID]

    except Exception as e:
        bot.reply_to(message, f"❌ خطأ:\n{e}")

# ================= RUN =================

def run_bot():
    print("🤖 Bot started")
    bot.remove_webhook()
    bot.infinity_polling(
        timeout=30,
        long_polling_timeout=30
    )

if __name
