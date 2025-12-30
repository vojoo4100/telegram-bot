import telebot
import os
import threading
from flask import Flask

# ====== CONFIG ======
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # عدل لو حابب
FILES_DIR = "files"

bot = telebot.TeleBot(TOKEN)
os.makedirs(FILES_DIR, exist_ok=True)

users_files = {}

# ====== TELEGRAM PART ======
@bot.message_handler(content_types=['document'])
def receive_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)

    file_name = message.document.file_name
    file_path = os.path.join(FILES_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(downloaded)

    users_files[file_name] = message.chat.id

    bot.reply_to(
        message,
        "✅ الملف وصل\n"
        "بعد ما تفكه ابعتهولي بنفس الاسم"
    )

@bot.message_handler(content_types=['document'])
def send_back_file(message):
    if message.from_user.id != ADMIN_ID:
        return

    file_name = message.document.file_name
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)

    file_path = os.path.join(FILES_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(downloaded)

    if file_name in users_files:
        user_id = users_files[file_name]
        with open(file_path, "rb") as f:
            bot.send_document(user_id, f)

        bot.reply_to(message, "✅ اتبعت للمستخدم")
    else:
        bot.reply_to(message, "❌ مش لاقي صاحب الملف")

# ====== KEEP ALIVE (RENDER FIX) ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    bot.infinity_polling(skip_pending=True)

# ====== START ======
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
