import telebot
import os
import time

# ====== الإعدادات ======
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # ✏️ حط ID بتاعك

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

# تخزين: اسم الملف -> ID المرسل
file_owners = {}

# ====== start ======
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 أهلاً بيك\n"
        "📎 ابعت الملف وهيوصل للإدمن\n"
        "📤 وهيرجعلك بعد التعديل"
    )

# ====== استقبال ملف من أي مستخدم ======
@bot.message_handler(content_types=["document"])
def receive_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        file_name = message.document.file_name
        file_path = os.path.join(FILES_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(downloaded)

        # حفظ صاحب الملف
        file_owners[file_name] = message.from_user.id

        # تأكيد للمرسل
        bot.reply_to(
            message,
            f"✅ تم استلام الملف\n"
            f"📄 {file_name}\n"
            f"⏳ في انتظار التعديل"
        )

        # إرسال الملف للإدمن
        with open(file_path, "rb") as f:
            bot.send_document(
                ADMIN_ID,
                f,
                caption=(
                    "📥 ملف جديد\n\n"
                    f"📄 الاسم: {file_name}\n"
                    f"👤 من ID: {message.from_user.id}\n\n"
                    "✏️ بعد التعديل ابعته هنا بنفس الاسم"
                )
            )

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error:\n{e}")

# ====== استقبال ملف من الأدمن ======
@bot.message_handler(content_types=["document"])
def receive_from_admin(message):
    if message.from_user.id != ADMIN_ID:
        return

    file_name = message.document.file_name

    if file_name not in file_owners:
        bot.reply_to(message, "❌ الملف ده مش معروف")
        return

    try:
        user_id = file_owners[file_name]

        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open(os.path.join(FILES_DIR, file_name), "wb") as f:
            f.write(downloaded)

        # إرسال الملف لصاحبه
        with open(os.path.join(FILES_DIR, file_name), "rb") as f:
            bot.send_document(
                user_id,
                f,
                caption="✅ تم تعديل ملفك وإرجاعه"
            )

        bot.reply_to(message, "📤 تم إرسال الملف لصاحبه بنجاح")

        # حذف من الذاكرة
        del file_owners[file_name]

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error:\n{e}")

# ====== تشغيل البوت ======
def run_bot():
    print("🤖 Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("❌ Error, restarting:", e)
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
