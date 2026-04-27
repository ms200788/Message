import os
import sqlite3
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 ENV variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# 🗄️ DB setup
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


# 📩 User → Admin
async def message_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not context.args:
        await update.message.reply_text("Usage: /message_admin <message>")
        return

    msg = " ".join(context.args)
    username = user.username or "No username"

    # Save
    cur.execute(
        "INSERT INTO messages (user_id, username, message, forwarded) VALUES (?, ?, ?, 0)",
        (user.id, username, msg)
    )
    conn.commit()

    await update.message.reply_text("Message saved!")

    # Try sending
    try:
        text = f"Username: @{username}\nID: {user.id}\n\nMessage: {msg}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=text)

        cur.execute("UPDATE messages SET forwarded=1 WHERE user_id=? AND message=?", (user.id, msg))
        conn.commit()

    except:
        pass


# 🔁 Retry unsent
async def resend_unsent(app):
    cur.execute("SELECT id, user_id, username, message FROM messages WHERE forwarded=0")
    rows = cur.fetchall()

    for msg_id, user_id, username, msg in rows:
        try:
            text = f"Username: @{username}\nID: {user_id}\n\nMessage: {msg}"
            await app.bot.send_message(chat_id=ADMIN_ID, text=text)

            cur.execute("UPDATE messages SET forwarded=1 WHERE id=?", (msg_id,))
            conn.commit()
        except:
            pass


# 🔁 Admin reply
async def reply_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /reply <user_id> <message>")
        return

    user_id = int(context.args[0])
    msg = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=user_id, text=f"Admin: {msg}")
        await update.message.reply_text("Sent ✅")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# 🤖 Telegram app
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("message_admin", message_admin))
application.add_handler(CommandHandler("reply", reply_user))


# 🌐 Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"


# ❤️ Health check
@app.route("/")
def home():
    return "Bot is alive"


# 🚀 Start
if __name__ == "__main__":
    import asyncio

    async def main():
        await application.initialize()
        await application.bot.set_webhook(WEBHOOK_URL)

        await resend_unsent(application)
        await application.start()

    asyncio.run(main())
    app.run(host="0.0.0.0", port=10000)
