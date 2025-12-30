import telebot
import os
from flask import Flask

# ============ CONFIG ============
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # ID بتاعك
# ================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ============ STATE ============
current_user_id = None
# ===============================

# ============ FLASK (Render) ============
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"
# =======================================

# ============ COMMANDS ============

@bot.message_handler(commands=["start"])
def start(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ البوت خاص")
        return

    bot.reply_to(
        message,
        "🎛️ <b>لوحة التحكم</b>\n\n"
        "/setuser ID ➜ تحديد المستخدم\n"
        "/who ➜ معرفة المستخدم الحالي\n"
        "/clear ➜ إلغاء التحديد\n\n"
        "📤 بعد التحديد ابعت أي حاجة"
    )

@bot.message_handler(commands=["setuser"])
def set_user(message):
    global current_user_id

    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])
        current_user_id = user_id
        bot.reply_to(message, f"✅ تم تحديد المستخدم:\n<code>{user_id}</code>")
    except:
        bot.reply_to(message, "❌ استخدم:\n/setuser 123456789")

@bot.message_handler(commands=["who"])
def who(message):
    if message.from_user.id != ADMIN_ID:
        return

    if current_user_id:
        bot.reply_to(message, f"👤 المستخدم الحالي:\n<code>{current_user_id}</code>")
    else:
        bot.reply_to(message, "❌ لا يوجد مستخدم محدد")

@bot.message_handler(commands=["clear"])
def clear_user(message):
    global current_user_id

    if message.from_user.id != ADMIN_ID:
        return

    current_user_id = None
    bot.reply_to(message, "🗑️ تم إلغاء التحديد")

# ============ FORWARD ANYTHING ============
@bot.message_handler(
    content_types=["text", "document", "photo", "video", "audio", "voice", "sticker"]
)
def forward_anything(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not current_user_id:
        bot.reply_to(message, "❌ حدد مستخدم الأول باستخدام /setuser")
        return

    try:
        bot.copy_message(
            chat_id=current_user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        bot.reply_to(message, "✅ تم الإرسال")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ:\n{e}")

# ============ RUN ============
def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    run_bot()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
