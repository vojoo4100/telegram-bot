import telebot
import os

# ============ CONFIG ============
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # حط ID الأدمن
# ================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# نخزن هنا: message_id بتاع الأدمن → user_id الأصلي
file_owners = {}

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 أهلاً بيك\n"
        "📎 ابعت الملف وهيروح للأدمن\n"
        "✏️ بعد التعديل هيرجعلك تلقائي"
    )

# ============ USER SEND FILE ============
@bot.message_handler(content_types=["document"])
def user_send_file(message):
    try:
        sent = bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=(
                "📁 <b>ملف جديد</b>\n"
                f"📄 الاسم: <code>{message.document.file_name}</code>\n"
                f"👤 من: @{message.from_user.username}\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
                "✏️ بعد التعديل ابعتهولي هنا"
            )
        )

        # نحفظ مين صاحب الملف
        file_owners[sent.message_id] = message.from_user.id

        bot.reply_to(message, "✅ الملف اتبعت للأدمن، استنى الرد")

    except Exception as e:
        bot.reply_to(message, "❌ حصل خطأ")
        bot.send_message(ADMIN_ID, f"⚠️ Error:\n{e}")

# ============ ADMIN SEND BACK ============
@bot.message_handler(
    func=lambda m: m.from_user.id == ADMIN_ID and m.reply_to_message is not None,
    content_types=["document", "text"]
)
def admin_send_back(message):
    replied_id = message.reply_to_message.message_id

    if replied_id not in file_owners:
        bot.reply_to(message, "❌ الرسالة دي مش مرتبطة بملف")
        return

    user_id = file_owners[replied_id]

    try:
        if message.content_type == "document":
            bot.send_document(user_id, message.document.file_id)

        elif message.content_type == "text":
            bot.send_message(user_id, message.text)

        bot.reply_to(message, "✅ اتبعت لصاحب الملف")

        # نمسحها بعد الإرسال
        del file_owners[replied_id]

    except Exception as e:
        bot.reply_to(message, f"❌ خطأ:\n{e}")

# ================= RUN =================
print("🤖 Bot is running...")
bot.infinity_polling(skip_pending=True)
