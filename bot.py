import os
import sqlite3
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

#🔐 ENV

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN)
app = Flask(name)

#🗄️ DB

conn = sqlite3.connect("messages.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
username TEXT,
message TEXT,
forwarded INTEGER DEFAULT 0
)
""")
conn.commit()

#📩 User → Admin

def message_admin(update, context):
user = update.effective_user

if not context.args:
    update.message.reply_text("Usage: /message_admin <message>")
    return

msg = " ".join(context.args)
username = user.username or "No username"

# Save
cur.execute(
    "INSERT INTO messages (user_id, username, message, forwarded) VALUES (?, ?, ?, 0)",
    (user.id, username, msg)
)
conn.commit()

update.message.reply_text("Message saved!")

try:
    text = f"Username: @{username}\nID: {user.id}\n\nMessage: {msg}"
    bot.send_message(chat_id=ADMIN_ID, text=text)

    cur.execute("UPDATE messages SET forwarded=1 WHERE user_id=? AND message=?", (user.id, msg))
    conn.commit()
except:
    pass

#🔁 Retry unsent on start

def resend_unsent():
cur.execute("SELECT id, user_id, username, message FROM messages WHERE forwarded=0")
rows = cur.fetchall()

for msg_id, user_id, username, msg in rows:
    try:
        text = f"Username: @{username}\nID: {user_id}\n\nMessage: {msg}"
        bot.send_message(chat_id=ADMIN_ID, text=text)

        cur.execute("UPDATE messages SET forwarded=1 WHERE id=?", (msg_id,))
        conn.commit()
    except:
        pass

#🔁 Admin → User

def reply_user(update, context):
if update.effective_user.id != ADMIN_ID:
return

if len(context.args) < 2:
    update.message.reply_text("Usage: /reply <user_id> <message>")
    return

user_id = int(context.args[0])
msg = " ".join(context.args[1:])

try:
    bot.send_message(chat_id=user_id, text=f"Admin: {msg}")
    update.message.reply_text("Sent ✅")
except Exception as e:
    update.message.reply_text(f"Error: {e}")

#🤖 Dispatcher

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("message_admin", message_admin))
dispatcher.add_handler(CommandHandler("reply", reply_user))

#🌐 Webhook

@app.route("/webhook", methods=["POST"])
def webhook():
update = Update.de_json(request.get_json(force=True), bot)
dispatcher.process_update(update)
return "ok"

#❤️ Health route (uptime)

@app.route("/")
def home():
return "Bot is alive"

#🚀 Startup

if name == "main":
bot.set_webhook(WEBHOOK_URL)
resend_unsent()