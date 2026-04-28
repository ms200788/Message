import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters



logging.basicConfig(
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
level=logging.INFO
)

logger = logging.getLogger(name)



BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not ADMIN_ID or not WEBHOOK_URL:
raise Exception("Missing ENV variables")

ADMIN_ID = int(ADMIN_ID)



app = Flask(name)



bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

Temporary memory (prevents duplicate sends)

processed_messages = set()



def start(update, context):
update.message.reply_text("✅ Bot is running!")

def message_admin(update, context):
msg = update.message

# prevent duplicate messages
if msg.message_id in processed_messages:
    return

processed_messages.add(msg.message_id)

user = msg.from_user
text = msg.text.replace("/message_admin", "").strip()

if not text:
    msg.reply_text("Send message like:\n/message_admin your text")
    return

forward_text = (
    f"👤 User: @{user.username}\n"
    f"🆔 ID: {user.id}\n\n"
    f"💬 Message:\n{text}"
)

context.bot.send_message(chat_id=ADMIN_ID, text=forward_text)
msg.reply_text("✅ Message sent to admin!")

def reply(update, context):
if update.message.from_user.id != ADMIN_ID:
return

args = context.args

if len(args) < 2:
    update.message.reply_text("Usage:\n/reply user_id message")
    return

try:
    user_id = int(args[0])
except:
    update.message.reply_text("Invalid user ID")
    return

text = " ".join(args[1:])

context.bot.send_message(chat_id=user_id, text=text)
update.message.reply_text("✅ Reply sent!")



dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("message_admin", message_admin))
dispatcher.add_handler(CommandHandler("reply", reply))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_admin))



@app.route("/")
def home():
return "🚀 Bot is running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
try:
data = request.get_json(force=True)
update = Update.de_json(data, bot)
dispatcher.process_update(update)
except Exception as e:
logger.error(f"Error processing update: {e}")
return "ok"



@app.before_first_request
def setup_webhook():
try:
webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
bot.set_webhook(webhook_url)
logger.info(f"Webhook set to: {webhook_url}")
except Exception as e:
logger.error(f"Webhook setup failed: {e}")