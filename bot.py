import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(name)
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

-------- Handlers --------

def start(update, context):
update.message.reply_text("Bot is running!")

def message_admin(update, context):
user = update.message.from_user
text = update.message.text.replace("/message_admin", "").strip()

msg = f"👤 @{user.username}\n🆔 {user.id}\n\n💬 {text}"
context.bot.send_message(chat_id=ADMIN_ID, text=msg)

def reply(update, context):
if str(update.message.from_user.id) != str(ADMIN_ID):
return

args = context.args
if len(args) < 2:
    update.message.reply_text("Usage: /reply user_id message")
    return

user_id = int(args[0])
text = " ".join(args[1:])

context.bot.send_message(chat_id=user_id, text=text)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("message_admin", message_admin))
dispatcher.add_handler(CommandHandler("reply", reply))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_admin))

-------- Flask routes --------

@app.route("/")
def home():
return "Bot running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
update = Update.de_json(request.get_json(force=True), bot)
dispatcher.process_update(update)
return "ok"

-------- Setup webhook --------

@app.before_first_request
def setup():
bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")