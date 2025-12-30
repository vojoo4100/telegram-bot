import telebot
import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # ← حط رقم تيلجرام بتاعك هنا

bot = telebot.TeleBot(TOKEN)
FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

users_files = {}

@bot.message_handler(content_types=['document'])
def receive_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)

    file_name = message.document.file_name
    file_path = os.path.join(FILES_DIR, file_name)

    with open(file_path, 'wb') as f:
        f.write(downloaded)

    users_files[file_name] = message.chat.id

    bot.reply_to(message, "تم استلام الملف ✅")
    bot.send_message(ADMIN_ID, f"📥 ملف جديد: {file_name}")

@bot.message_handler(commands=['send'])
def send_back(message):
    if message.chat.id != ADMIN_ID:
        return

    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "رد على الملف المفكوك وبعت /send")
        return

    doc = message.reply_to_message.document
    file_name = doc.file_name

    if file_name not in users_files:
        bot.reply_to(message, "مش لاقي صاحب الملف")
        return

    user_id = users_files[file_name]

    file_info = bot.get_file(doc.file_id)
    downloaded = bot.download_file(file_info.file_path)

    with open(file_name, 'wb') as f:
        f.write(downloaded)

    with open(file_name, 'rb') as f:
        bot.send_document(user_id, f)

    os.remove(file_name)
    bot.reply_to(message, "اتبعَت للمستخدم ✅")

bot.infinity_polling()
