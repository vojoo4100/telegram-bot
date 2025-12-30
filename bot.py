import telebot
import os

# ================= CONFIG =================
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # ✏️ حط ID بتاعك
# =========================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# تخزين مؤقت: اسم الملف -> user_id
file_owners = {}

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🔥 اسكربت فك جميع الكونفجات 🔥\n\n"
        "📎 ابعت الملف 👇"
    )

# ================= DOCUMENT HANDLER =================
@bot.message_handler(content_types=["document"])
def handle_document(message):
    file_name = message.document.file_name
    sender_id = message.from_user.id

    # ===== لو مستخدم عادي =====
    if sender_id != ADMIN_ID:
        file_owners[file_name] = sender_id

        bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=(
                "📁 <b>ملف جديد</b>\n\n"
                f"📄 الاسم: {file_name}\n"
                f"🆔 ID: {sender_id}\n\n"
                "✏️ بعد ما تفكه ابعته بنفس الاسم"
            )
        )

        bot.reply_to(
            message,
            "✅ الملف وصل\n"
            "بعد ما تفكه ابعتهولي بنفس الاسم"
        )
        return

    # ===== لو إدمن =====
    if file_name not in file_owners:
        bot.reply_to(message, "❌ الملف ده مش معروف")
        return

    user_id = file_owners[file_name]

    bot.send_document(
        user_id,
        message.document.file_id,
        caption="✅ تم فك الملف وإرجاعه ليك"
    )

    bot.reply_to(message, "📤 تم إرسال الملف لصاحبه")

    del file_owners[file_name]

# ================= RUN =================
print("🤖 Bot is running...")
bot.infinity_polling(timeout=30, long_polling_timeout=30)
