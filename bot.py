import telebot
import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # ID بتاعك

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# نخزن الربط هنا
message_map = {}

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🔥 اسكربت فك جميع الكونفجات 🔥\n\n"
        "📎 ابعت الملف 👇"
    )

# ================= استقبال ملف من مستخدم =================
@bot.message_handler(content_types=["document"])
def receive_from_user(message):
    if message.from_user.id == ADMIN_ID:
        return

    sent = bot.forward_message(
        ADMIN_ID,
        message.chat.id,
        message.message_id
    )

    message_map[sent.message_id] = message.from_user.id

    bot.reply_to(
        message,
        "✅ الملف وصل\n"
        "بعد ما تفكه ابعتهولي بنفس الاسم ✏️"
    )

# ================= رد الأدمن بملف =================
@bot.message_handler(content_types=["document"])
def admin_reply_document(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        return

    replied_msg_id = message.reply_to_message.message_id

    if replied_msg_id not in message_map:
        bot.reply_to(message, "❌ الرد ده مش مرتبط بمستخدم")
        return

    user_id = message_map[replied_msg_id]

    bot.send_document(
        user_id,
        message.document.file_id,
        caption="✅ تم فك الملف وإرجاعه ليك"
    )

    bot.reply_to(message, "📤 الملف اتبعت لصاحبه")
    del message_map[replied_msg_id]

# ================= رد الأدمن بنص =================
@bot.message_handler(content_types=["text"])
def admin_reply_text(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        return

    replied_msg_id = message.reply_to_message.message_id

    if replied_msg_id not in message_map:
        return

    user_id = message_map[replied_msg_id]

    bot.send_message(
        user_id,
        f"📩 رسالة من الأدمن:\n{message.text}"
    )

    bot.reply_to(message, "📤 الرسالة اتبعتت")
    del message_map[replied_msg_id]

# ================= RUN =================
print("🤖 Bot running...")
bot.infinity_polling(timeout=30, long_polling_timeout=30)
