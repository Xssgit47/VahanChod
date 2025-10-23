# ============================================================
# 🚗 Vehicle Info Telegram Bot
# 👑 Author: @FNxDANGER
# 💻 VPS Ready | .env | Force Join | Admin Controls | User Tracking
# ============================================================

import os
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ===============================
# ⚙️ CONFIGURATION
# ===============================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
FORCE_CHANNEL_ID = int(os.getenv("FORCE_CHANNEL_ID", "-1002706074038"))  # your channel ID

DATA_FILE = "users.json"
START_TIME = time.time()

# ===============================
# 🧾 LOGGING
# ===============================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===============================
# 💾 USER DATABASE
# ===============================
def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

# ===============================
# 🧩 FORCE JOIN CHECK
# ===============================
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        member = await context.bot.get_chat_member(FORCE_CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"Membership check failed for {user_id}: {e}")
        return False

async def ask_to_join(update: Update):
    join_btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🚀 Join Channel", url="https://t.me/DANGERxAHEAD")]]
    )
    await update.message.reply_text(
        "⚠️ You must join our channel to use this bot!\n\n"
        "🔗 Join here: @DANGERxAHEAD",
        reply_markup=join_btn
    )

# ===============================
# 🔍 VEHICLE DATA FETCHER
# ===============================
def fetch_vehicle_data(num):
    ua = generate_user_agent()
    headers = {"User-Agent": ua}
    url = f"https://vahanx.in/rc-search/{num}"

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"Error": "Failed to connect to the data source."}

    data = {
        "Owner Name": None, "Father's Name": None, "Owner Serial No": None,
        "Model Name": None, "Maker Model": None, "Vehicle Class": None,
        "Fuel Type": None, "Fuel Norms": None, "Registration Date": None,
        "Insurance Company": None, "Insurance No": None, "Insurance Expiry": None,
        "Insurance Upto": None, "Fitness Upto": None, "Tax Upto": None,
        "PUC No": None, "PUC Upto": None, "Financier Name": None,
        "Registered RTO": None, "Address": None, "City Name": None, "Phone": None
    }

    for label in data:
        div = soup.find("span", string=label)
        if div:
            parent_div = div.find_parent("div")
            if parent_div:
                p_tag = parent_div.find("p")
                if p_tag:
                    data[label] = p_tag.get_text(strip=True)
    return data

# ===============================
# 🤖 COMMAND HANDLERS
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await ask_to_join(update)
        return

    user = update.message.from_user
    add_user(user.id)
    msg = (
        f"👋 Hello {user.first_name}!\n\n"
        "Send me a vehicle number like `MH12AB1234`\n"
        "and I’ll fetch its registration details for you.\n\n"
        "⚡ _Powered By @FNxDANGER_"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await ask_to_join(update)
        return

    help_text = (
        "🆘 *Help Menu*\n\n"
        "Available commands:\n"
        "`/start` - Start the bot\n"
        "`/help` - Show this help message\n"
        "`/ping` - Check bot status\n"
        "`/commands` - List all commands\n"
        "`/status` - Admin only: View usage stats\n"
        "`/broadcast` - Admin only: Send message to all users\n\n"
        "👑 Developer: @FNxDANGER"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await ask_to_join(update)
        return

    cmds = (
        "📜 *Command List*\n\n"
        "`/start` - Start the bot\n"
        "`/help` - Show help\n"
        "`/ping` - Check bot response\n"
        "`/commands` - List all commands\n"
        "`/status` - (Admin Only)\n"
        "`/broadcast` - (Admin Only)\n\n"
        "⚡ _Powered By @FNxDANGER_"
    )
    await update.message.reply_text(cmds, parse_mode="Markdown")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await ask_to_join(update)
        return

    uptime = time.time() - START_TIME
    hours, rem = divmod(int(uptime), 3600)
    mins, secs = divmod(rem, 60)
    msg = f"🏓 Pong! Bot is alive.\n⏱ Uptime: {hours}h {mins}m {secs}s\n⚡ _Powered By @FNxDANGER_"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    users = load_users()
    uptime = int(time.time() - START_TIME)
    msg = (
        f"📊 *Bot Status*\n\n"
        f"👥 Total Users: {len(users)}\n"
        f"🕒 Uptime: {uptime // 60} minutes\n"
        f"⚡ _Powered By @FNxDANGER_"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage: `/broadcast your_message_here`", parse_mode="Markdown")
        return

    msg = " ".join(context.args)
    users = load_users()
    count = 0

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 *Broadcast:*\n\n{msg}\n\n⚡ _Powered By @FNxDANGER_", parse_mode="Markdown")
            count += 1
        except Exception as e:
            logger.warning(f"Failed to send to {user_id}: {e}")

    await update.message.reply_text(f"✅ Broadcast sent to {count}/{len(users)} users.", parse_mode="Markdown")

# ===============================
# 🔍 HANDLE VEHICLE NUMBER TEXT
# ===============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        await ask_to_join(update)
        return

    user = update.message.from_user
    add_user(user.id)
    num = update.message.text.strip().upper()

    await update.message.reply_text(f"🔍 Searching for *{num}*...\n⚡ _Powered By @FNxDANGER_", parse_mode="Markdown")

    data = fetch_vehicle_data(num)
    if not any(data.values()):
        await update.message.reply_text("❌ No data found. Please check the number.\n⚡ _Powered By @FNxDANGER_", parse_mode="Markdown")
        return

    result = "\n".join([f"*{k}:* {v or 'N/A'}" for k, v in data.items()])
    final = f"🚗 *Vehicle Details:*\n\n{result}\n\n⚡ _Powered By @FNxDANGER_"
    await update.message.reply_text(final, parse_mode="Markdown")

# ===============================
# 🧠 MAIN FUNCTION
# ===============================
async def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN is missing in .env")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("commands", commands))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Bot running | Force Join Enabled | Powered By @FNxDANGER")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Bot stopped manually.")
