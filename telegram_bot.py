from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from AdviewScriptbyYash import AdViewBot
import threading
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1329609274

CHANNELS = ["@Earning_Key", "@surbhiscripter", "@EagletekTelegram"]

USER_STATE = {}
USER_DATA = {}
STOP_USERS = {}

# -------- FORCE JOIN --------
def is_user_joined(bot, user_id):
    for ch in CHANNELS:
        try:
            m = bot.get_chat_member(ch, user_id)
            if m.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True


def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Channel 1", url="https://t.me/Earning_Key")],
        [InlineKeyboardButton("Join Channel 2", url="https://t.me/surbhiscripter")],
        [InlineKeyboardButton("Join Channel 3", url="https://t.me/EagletekTelegram")]
    ])


# -------- COMMANDS --------
def start(update, context):
    update.message.reply_text(
        "Welcome to AdView Bot 🚀\n\n"
        "/run – Start earning\n"
        "/cancel – Stop process"
    )


def run(update, context):
    uid = update.message.from_user.id

    if not is_user_joined(context.bot, uid):
        update.message.reply_text(
            "❌ Join all channels first:",
            reply_markup=join_buttons()
        )
        return

    USER_STATE[uid] = "MOBILE"
    update.message.reply_text("📱 Send mobile number")


def cancel(update, context):
    uid = update.message.from_user.id
    STOP_USERS[uid] = True
    USER_STATE.pop(uid, None)
    USER_DATA.pop(uid, None)
    update.message.reply_text("🛑 Stopped")


# -------- MESSAGE FLOW --------
def handle_message(update, context):
    uid = update.message.from_user.id
    text = update.message.text

    if USER_STATE.get(uid) == "MOBILE":
        USER_DATA[uid] = {"mobile": text}
        USER_STATE[uid] = "PASSWORD"
        update.message.reply_text("🔒 Send password")
        return

    if USER_STATE.get(uid) == "PASSWORD":
        password = text
        mobile = USER_DATA[uid]["mobile"]
        USER_STATE.pop(uid)

        try:
            context.bot.delete_message(update.message.chat_id, update.message.message_id)
        except:
            pass

        STOP_USERS[uid] = False

        def is_stopped():
            return STOP_USERS.get(uid, False)

        def task():
            bot = AdViewBot(mobile, password, is_stopped)
            bot.run()
            if not STOP_USERS.get(uid):
                context.bot.send_message(uid, "✅ Session finished")

        threading.Thread(target=task, daemon=True).start()


# -------- BOT START --------
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("run", run))
dp.add_handler(CommandHandler("cancel", cancel))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
updater.idle()
