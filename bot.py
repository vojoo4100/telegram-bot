import telebot
import os

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # ID بتاعك
# =========================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ربط رسالة الأدمن برسالة المستخدم
reply_map = {}

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🔥 اسكربت فك جميع الكونفجات 🔥\n\n"
        "📎 ابعت الملف 👇"
    )

# ================= استقبال الملفات =================
@bot.message_handler(content_types=["document"])
def handle_document(message):
    sender_id = message.from_user.id

    # ===== مستخدم عادي =====
    if sender_id != ADMIN_ID:
        sent = bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=(
                "📁 <b>ملف جديد</b>\n\n"
                f"👤 ID: {sender_id}\n\n"
                "✏️ اعمل Reply على الرسالة دي عشان تبعت الرد"
            )
        )

        # ربط رسالة الأدمن بالمستخدم
        reply_map[sent.message_id] = sender_id

        bot.reply_to(
            message,
            "✅ الملف وصل\n"
            "بعد ما تفكه ابعتهولي Reply على نفس الرسالة"
        )
        return

    # ===== أدمن بيرد بملف =====
    if message.reply_to_message:
        replied_id = message.reply_to_message.message_id

        if replied_id not in reply_map:
            bot.reply_to(message, "❌ الرد ده مش مرتبط بمستخدم")
            return

        user_id = reply_map[replied_id]

        bot.send_document(
            user_id,
            message.document.file_id,
            caption="✅ تم فك الملف وإرجاعه ليك"
        )

        bot.reply_to(message, "📤 الملف اتبعت لصاحبه")
        del reply_map[replied_id]

# ================= رد نصي من الأدمن =================
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        return

    replied_id = message.reply_to_message.message_id

    if replied_id not in reply_map:
        return

    user_id = reply_map[replied_id]

    bot.send_message(user_id, f"📩 رسالة من الأدمن:\n{message.text}")
    bot.reply_to(message, "📤 الرسالة اتبعتت")

    del reply_map[replied_id]

# ================= RUN =================
print("🤖 Bot is running...")
bot.infinity_polling(timeout=30, long_polling_timeout=30)
