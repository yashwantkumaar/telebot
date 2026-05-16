import telebot
from telebot import types
from dotenv import load_dotenv
import os
import time
import json

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# CONFIG
# =========================
WEBSITE_URL = "https://truthordarewithfrndss.netlify.app/"

USERS_FILE = "users.txt"
SEARCH_FILE = "searches.json"

# =========================
# STARTUP MESSAGE
# =========================
print("""
====================================
🔥 TrendBoost Bot Started Successfully
🚀 Bot is Running...
====================================
""")

# =========================
# SAVE USERS
# =========================
def save_user(user_id):

    user_id = str(user_id)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            pass

    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()

    if user_id not in users:
        with open(USERS_FILE, "a") as f:
            f.write(user_id + "\n")


# =========================
# GET USERS
# =========================
def get_users():

    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE, "r") as f:
        return f.read().splitlines()


# =========================
# LOAD SEARCHES
# =========================
def load_searches():

    if not os.path.exists(SEARCH_FILE):
        return {}

    with open(SEARCH_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}


# =========================
# SAVE SEARCHES
# =========================
def save_searches(data):

    with open(SEARCH_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# START COMMAND
# =========================
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    save_user(user_id)

    # Loading Effect
    loading = bot.send_message(
        message.chat.id,
        "🔄 Connecting..."
    )

    time.sleep(1)

    bot.edit_message_text(
        "✅ Connected Successfully!",
        message.chat.id,
        loading.message_id
    )

    # Buttons
    markup = types.InlineKeyboardMarkup()

    website_btn = types.InlineKeyboardButton(
        "🚀 Open Website",
        url=WEBSITE_URL
    )

    trending_btn = types.InlineKeyboardButton(
        "🔥 Trending Searches",
        callback_data="trending"
    )

    markup.add(website_btn)
    markup.add(trending_btn)

    # Welcome Message
    welcome_text = """
🔥 *Welcome to TrendBoost Bot!*

Search anything to make it trending 🚀

✨ Movies
✨ Anime
✨ IPL
✨ Web Series
✨ Viral Content

Powered by TrendBoost 🚀
"""

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=markup
    )


# =========================
# TRENDING CALLBACK
# =========================
@bot.callback_query_handler(func=lambda call: call.data == "trending")
def trending_callback(call):

    searches = load_searches()

    sorted_keywords = sorted(
        searches.items(),
        key=lambda x: x[1],
        reverse=True
    )

    if not sorted_keywords:

        bot.answer_callback_query(
            call.id,
            "No searches yet!"
        )
        return

    msg = "🔥 *Top Trending Searches*\n\n"

    for i, (word, count) in enumerate(sorted_keywords[:10], start=1):
        msg += f"{i}. {word} — {count} searches\n"

    bot.send_message(
        call.message.chat.id,
        msg,
        parse_mode="Markdown"
    )


# =========================
# USERS COMMAND
# =========================
@bot.message_handler(commands=['users'])
def users_count(message):

    if message.from_user.id != ADMIN_ID:
        return

    total = len(get_users())

    bot.reply_to(
        message,
        f"👥 Total Users: {total}"
    )


# =========================
# BROADCAST COMMAND
# =========================
@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    msg = message.text.replace("/broadcast", "").strip()

    if not msg:

        bot.reply_to(
            message,
            "❌ Usage:\n/broadcast Your Message"
        )
        return

    users = get_users()

    sent = 0

    for user in users:
        try:
            bot.send_message(user, f"📢 {msg}")
            sent += 1
        except:
            pass

    bot.reply_to(
        message,
        f"✅ Broadcast sent to {sent} users"
    )


# =========================
# TRENDING COMMAND
# =========================
@bot.message_handler(commands=['trending'])
def trending(message):

    searches = load_searches()

    sorted_keywords = sorted(
        searches.items(),
        key=lambda x: x[1],
        reverse=True
    )

    if not sorted_keywords:

        bot.reply_to(
            message,
            "❌ No searches yet."
        )
        return

    msg = "🔥 *Top Trending Searches*\n\n"

    for i, (word, count) in enumerate(sorted_keywords[:10], start=1):
        msg += f"{i}. {word} — {count} searches\n"

    bot.send_message(
        message.chat.id,
        msg,
        parse_mode="Markdown"
    )


# =========================
# TRACK SEARCHES
# =========================
@bot.message_handler(func=lambda message: True)
def track_search(message):

    text = message.text.lower()

    # Ignore commands
    if text.startswith("/"):
        return

    searches = load_searches()

    if text in searches:
        searches[text] += 1
    else:
        searches[text] = 1

    save_searches(searches)

    markup = types.InlineKeyboardMarkup()

    website_btn = types.InlineKeyboardButton(
        "🚀 Visit Website",
        url=WEBSITE_URL
    )

    markup.add(website_btn)

    bot.reply_to(
        message,
        f"""
🔍 *Search Recorded*

You searched:
`{text}`

🔥 This keyword is now added to trending searches.
""",
        parse_mode="Markdown",
        reply_markup=markup
    )


# =========================
# RUN BOT
# =========================
print("🚀 Bot Polling Started...")

bot.infinity_polling(skip_pending=True)