from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import threading, time, json, os
from adview_runner import run_adview

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "users.json"

# 🔔 FORCE JOIN CHANNELS (UPDATED)
CHANNELS = ["@Earning_Key", "@surbhiscripter", "@EagletekTelegram"]

# ---------- FORCE JOIN ----------
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
    keyboard = []
    for ch in CHANNELS:
        keyboard.append(
            [InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
        )
    return InlineKeyboardMarkup(keyboard)

# ---------- LOAD / SAVE USERS ----------
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

USERS = load_users()

# ---------- COMMANDS ----------
def start(update, context):
    uid = update.effective_user.id

    if not is_user_joined(context.bot, uid):
        update.message.reply_text(
            "❌ Join All the Channels:",
            reply_markup=join_buttons()
        )
        return

    update.message.reply_text(
        "🤖 Auto AdView Bot\n\n"
        "Steps to use: https://t.me/Earning_Key/4413\n\n"
        "👉 Save account:\n"
        "/save mobile password\n\n"
        "👉 Stop auto run:\n"
        "/stop"
    )

def save(update, context):
    uid = update.effective_user.id

    if not is_user_joined(context.bot, uid):
        update.message.reply_text(
            "❌ Pehle sabhi channels join karo:",
            reply_markup=join_buttons()
        )
        return

    try:
        mobile = context.args[0]
        password = context.args[1]

        USERS[str(uid)] = {
            "mobile": mobile,
            "password": password,
            "auto": True
        }
        save_users(USERS)

        update.message.reply_text("✅ Saved. Auto run enabled (hourly).")
    except:
        update.message.reply_text("❌ Use: /save mobile password")

def stop(update, context):
    uid = str(update.effective_user.id)
    if uid in USERS:
        USERS[uid]["auto"] = False
        save_users(USERS)
        update.message.reply_text("⛔ Auto run stopped")

# ---------- HOURLY RUNNER ----------
def auto_runner(bot):
    while True:
        for uid, data in USERS.items():
            if data.get("auto"):
                try:
                    result = run_adview(data["mobile"], data["password"])
                    bot.send_message(chat_id=int(uid), text=result)
                except:
                    pass
        time.sleep(3600)  # 1 hour

# ---------- MAIN ----------
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("save", save))
    dp.add_handler(CommandHandler("stop", stop))

    updater.start_polling()

    threading.Thread(
        target=auto_runner,
        args=(updater.bot,),
        daemon=True
    ).start()

    updater.idle()

if __name__ == "__main__":
    main()
