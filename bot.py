import os
import logging
from queue import Queue

from flask import Flask, request, Response
from telegram import Bot, Update, ParseMode
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    Filters
)

# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ==================================================
# ENV VARIABLES
# ==================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

if not ADMIN_ID:
    raise Exception("ADMIN_ID missing")

if not WEBHOOK_URL:
    raise Exception("WEBHOOK_URL missing")

ADMIN_ID = int(ADMIN_ID)

# ==================================================
# FLASK + TELEGRAM INIT
# ==================================================

app = Flask(__name__)

bot = Bot(token=BOT_TOKEN)

update_queue = Queue()

dispatcher = Dispatcher(
    bot,
    update_queue,
    use_context=True
)

# ==================================================
# ANTI DUPLICATE
# ==================================================

processed_messages = set()

# ==================================================
# HTML PAGE
# ==================================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

  <meta charset="UTF-8" />

  <meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
  />

  <title>Support Page</title>

  <style>

    *{
      margin:0;
      padding:0;
      box-sizing:border-box;
      font-family:Arial,sans-serif;
    }

    body{
      background:black;
      color:white;
      min-height:100vh;
      overflow-x:hidden;
      position:relative;
    }

    /* STARS */

    .stars{
      position:fixed;
      width:100%;
      height:100%;
      top:0;
      left:0;
      z-index:-1;
      overflow:hidden;
    }

    .star{
      position:absolute;
      background:white;
      border-radius:50%;
      animation:twinkle 2s infinite ease-in-out;
    }

    @keyframes twinkle{

      0%,100%{
        opacity:0.2;
        transform:scale(1);
      }

      50%{
        opacity:1;
        transform:scale(1.8);
      }

    }

    /* TOP BAR */

    .topbar{
      width:100%;
      padding:18px;
      text-align:center;
      font-size:28px;
      font-weight:bold;
      background:rgba(255,255,255,0.06);
      backdrop-filter:blur(5px);
      border-bottom:1px solid rgba(255,255,255,0.15);
      letter-spacing:2px;
    }

    /* MAIN CONTAINER */

    .container{
      width:90%;
      max-width:850px;
      margin:35px auto;
      display:flex;
      flex-direction:column;
      gap:25px;
    }

    /* DESCRIPTION */

    .description{
      background:rgba(255,255,255,0.06);
      border:1px solid rgba(255,255,255,0.12);
      border-radius:18px;
      padding:25px;
      line-height:1.7;
      font-size:17px;
      box-shadow:0 0 20px rgba(255,255,255,0.05);
    }

    /* NOTICE WRAPPER */

    .notice-wrapper{
      display:grid;
      grid-template-columns:1fr 1fr;
      gap:20px;
    }

    /* NOTICE BOX */

    .notice{
      background:rgba(255,255,255,0.05);
      border:1px solid rgba(255,255,255,0.12);
      border-radius:16px;
      padding:20px;
      transition:0.3s;
    }

    .notice:hover{
      transform:translateY(-4px);
      box-shadow:0 0 15px rgba(255,255,255,0.12);
    }

    .notice h3{
      margin-bottom:12px;
      font-size:20px;
    }

    .notice p{
      color:#d0d0d0;
      line-height:1.5;
    }

    /* BOTTOM BOX */

    .bottom-box{
      background:rgba(255,255,255,0.06);
      border:1px solid rgba(255,255,255,0.12);
      border-radius:18px;
      padding:28px;
      text-align:center;
      font-size:18px;
      line-height:1.7;
      box-shadow:0 0 20px rgba(255,255,255,0.05);
    }

    /* MOBILE */

    @media(max-width:700px){

      .notice-wrapper{
        grid-template-columns:1fr;
      }

      .topbar{
        font-size:24px;
      }

    }

  </style>

</head>

<body>

  <!-- STARS -->
  <div class="stars" id="stars"></div>

  <!-- TOP BAR -->
  <div class="topbar">
    SUPPORT
  </div>

  <!-- CONTENT -->
  <div class="container">

    <!-- DESCRIPTION -->
    <div class="description">

      Welcome to our support page.

      Here you can find updates,
      notices, and help regarding our services.

      We are committed to providing smooth
      and reliable assistance whenever needed.

    </div>

    <!-- NOTICE BOXES -->
    <div class="notice-wrapper">

      <div class="notice">

        <h3>Notice 1</h3>

        <p>
          Maintenance updates may occur during
          late night hours.

          Some services could be temporarily unavailable.
        </p>

      </div>

      <div class="notice">

        <h3>Notice 2</h3>

        <p>
          Please keep your app updated
          to receive the latest features,
          fixes, and security improvements.
        </p>

      </div>

    </div>

    <!-- BOTTOM BOX -->
    <div class="bottom-box">

      Need more help?

      Contact our support team anytime
      for assistance, feedback, or issue reporting.

    </div>

  </div>

  <!-- STARS SCRIPT -->

  <script>

    const starsContainer =
      document.getElementById("stars");

    for(let i = 0; i < 180; i++){

      const star =
        document.createElement("div");

      star.classList.add("star");

      star.style.top =
        Math.random() * 100 + "%";

      star.style.left =
        Math.random() * 100 + "%";

      const size =
        Math.random() * 3 + 1;

      star.style.width =
        size + "px";

      star.style.height =
        size + "px";

      star.style.animationDuration =
        (Math.random() * 3 + 2) + "s";

      star.style.animationDelay =
        Math.random() * 5 + "s";

      starsContainer.appendChild(star);

    }

  </script>

</body>
</html>
"""

# ==================================================
# START COMMAND
# ==================================================

def start(update, context):

    support_link = f"{WEBHOOK_URL}/support"

    update.message.reply_text(
        f"🌐 Support Page:\n{support_link}"
    )

# ==================================================
# MESSAGE ADMIN
# ==================================================

def message_admin(update, context):

    msg = update.message

    if not msg:
        return

    if not msg.text:
        return

    # prevent duplicate
    if msg.message_id in processed_messages:
        return

    processed_messages.add(msg.message_id)

    user = msg.from_user

    first_name = user.first_name or ""
    last_name = user.last_name or ""

    full_name = (
        first_name + " " + last_name
    ).strip()

    # display username or clickable name
    if user.username:

        user_display = f"@{user.username}"

    else:

        user_display = (
            f"<a href='tg://user?id={user.id}'>"
            f"{full_name}"
            f"</a>"
        )

    text = msg.text.replace(
        "/message_admin",
        ""
    ).strip()

    if not text:

        msg.reply_text(
            "Send message like:\n"
            "/message_admin hello"
        )

        return

    forward_text = (
        f"👤 User: {user_display}\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"💬 Message:\n{text}"
    )

    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=forward_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    msg.reply_text(
        "✅ Message sent to admin!"
    )

# ==================================================
# REPLY COMMAND
# ==================================================

def reply(update, context):

    if update.message.from_user.id != ADMIN_ID:
        return

    args = context.args

    if len(args) < 2:

        update.message.reply_text(
            "Usage:\n/reply user_id message"
        )

        return

    try:

        user_id = int(args[0])

    except:

        update.message.reply_text(
            "Invalid user ID"
        )

        return

    text = " ".join(args[1:])

    context.bot.send_message(
        chat_id=user_id,
        text=text
    )

    update.message.reply_text(
        "✅ Reply sent!"
    )

# ==================================================
# HANDLERS
# ==================================================

dispatcher.add_handler(
    CommandHandler("start", start)
)

dispatcher.add_handler(
    CommandHandler(
        "message_admin",
        message_admin
    )
)

dispatcher.add_handler(
    CommandHandler("reply", reply)
)

dispatcher.add_handler(
    MessageHandler(
        Filters.text & ~Filters.command,
        message_admin
    )
)

# ==================================================
# ROUTES
# ==================================================

@app.route("/")
def home():

    return "🚀 Bot is running!"

# SUPPORT PAGE

@app.route("/support")
def support_page():

    return Response(
        HTML_PAGE,
        mimetype="text/html"
    )

# TELEGRAM WEBHOOK

@app.route(
    f"/{BOT_TOKEN}",
    methods=["POST"]
)
def webhook():

    try:

        data = request.get_json(force=True)

        update = Update.de_json(
            data,
            bot
        )

        dispatcher.process_update(update)

    except Exception as e:

        logger.error(
            f"Error processing update: {e}"
        )

    return "ok"

# ==================================================
# SET WEBHOOK
# ==================================================

@app.before_first_request
def setup_webhook():

    try:

        webhook_url = (
            f"{WEBHOOK_URL}/{BOT_TOKEN}"
        )

        bot.delete_webhook()

        bot.set_webhook(webhook_url)

        logger.info(
            f"Webhook set to: {webhook_url}"
        )

    except Exception as e:

        logger.error(
            f"Webhook setup failed: {e}"
        )

# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )