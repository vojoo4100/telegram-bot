import telebot
import os
import threading
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5778768733  # عدلها لو لزم
bot = telebot.TeleBot(TOKEN)

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

users_files = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "ابعت الملف 👇")

@bot.message_handler(content_types=['document'])
def receive_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)

    file_name = message.document.file_name
    file_path = os.path.join(FILES_DIR, file_name)

    with open(file_path, 'wb') as f:
        f.write(downloaded)

    users_files[file_name] = message.chat.id

    bot.send_message(
        message.chat.id,
        "✅ الملف وصل\nبعد ما تفكه ابعتهولي بنفس الاسم"
    )

@bot.message_handler(func=lambda m: m.document and m.from_user.id == ADMIN_ID)
def admin_send_back(message):
    file_name = message.document.file_name

    if file_name not in users_files:
        bot.send_message(message.chat.id, "❌ مفيش مستخدم مستني الملف ده")
        return

    user_id = users_files[file_name]
    bot.send_document(user_id, message.document.file_id)
    bot.send_message(message.chat.id, "✅ اتبعت للمستخدم")

# ---------- Flask fake server (عشان Render) ----------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---------- Run ----------
threading.Thread(target=run_flask).start()
bot.infinity_polling()
