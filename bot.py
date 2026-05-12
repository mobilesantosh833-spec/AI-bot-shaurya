import telebot
from groq import Groq

# ==================== APNI DETAILS YAHAN BHARO ====================
BOT_TOKEN = "bot_token"
GROQ_API_KEY = "GROQ_API_KEY"
OWNER_ID = "owner id "
# ==================================================================

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

user_histories = {}
banned_users = set()

# ======================== /start ========================
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.reply_to(message, f"""
👋 ("*Jai shree ram {name}!*)

Main tumhara personal AI Assistant hun 🤖

📌 *Commands:*
/start - Bot shuru karo
/reset - Chat history clear karo
/help - Help dekho
/owner - Owner info

💬 Bas kuch bhi likho, main jawab dunga!
    """, parse_mode="Markdown")

# ======================== /help ========================
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, """
🆘 *Help Menu*

/start - Bot restart karo
/reset - Purani chat bhula do
/owner - Owner kaun hai
/help - Ye menu dekho

💬 Koi bhi sawaal seedha likho!
    """, parse_mode="Markdown")

# ======================== /reset ========================
@bot.message_handler(commands=['reset'])
def reset(message):
    user_id = message.from_user.id
    user_histories[user_id] = []
    bot.reply_to(message, "🔄 Chat history clear ho gayi! Naya sawaal pucho.")

# ======================== /owner ========================
@bot.message_handler(commands=['owner'])
def owner_cmd(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "👑 *Tum hi ho is bot ke MALIK!*", parse_mode="Markdown")
    else:
        bot.reply_to(message, "🔒 Tum owner nahi ho!")

# ======================== /stats (Owner Only) ========================
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Ye command sirf owner ke liye hai!")
        return
    total_users = len(user_histories)
    total_banned = len(banned_users)
    bot.reply_to(message, f"""
📊 *Bot Stats:*
👥 Total Users: {total_users}
🚫 Banned Users: {total_banned}
    """, parse_mode="Markdown")

# ======================== /broadcast (Owner Only) ========================
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Sirf owner broadcast kar sakta hai!")
        return
    text = message.text.replace('/broadcast', '').strip()
    if not text:
        bot.reply_to(message, "⚠️ Example: /broadcast Hello sabko!")
        return
    success = 0
    for user_id in user_histories:
        try:
            bot.send_message(user_id, f"📢 *Owner ka Message:*\n{text}", parse_mode="Markdown")
            success += 1
        except:
            pass
    bot.reply_to(message, f"✅ {success} logon ko message bhej diya!")

# ======================== /ban (Owner Only) ========================
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Sirf owner ban kar sakta hai!")
        return
    try:
        ban_id = int(message.text.split()[1])
        banned_users.add(ban_id)
        bot.reply_to(message, f"🚫 User {ban_id} ban ho gaya!")
    except:
        bot.reply_to(message, "⚠️ Example: /ban 123456789")

# ======================== /unban (Owner Only) ========================
@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Sirf owner unban kar sakta hai!")
        return
    try:
        unban_id = int(message.text.split()[1])
        banned_users.discard(unban_id)
        bot.reply_to(message, f"✅ User {unban_id} unban ho gaya!")
    except:
        bot.reply_to(message, "⚠️ Example: /unban 123456789")

# ======================== /myid ========================
@bot.message_handler(commands=['myid'])
def my_id(message):
    uid = message.from_user.id
    bot.reply_to(message, f"🆔 Tumhara Telegram ID: `{uid}`", parse_mode="Markdown")

# ======================== AI REPLY ========================
@bot.message_handler(func=lambda message: True)
def ai_reply(message):
    user_id = message.from_user.id

    if user_id in banned_users:
        bot.reply_to(message, "🚫 Tum ban ho! Owner se contact karo.")
        return

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({
        "role": "user",
        "content": message.text
    })

    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]

    try:
        bot.send_chat_action(message.chat.id, 'typing')

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Tum ek helpful AI assistant ho. Hinglish mein baat karo (Hindi + English mix). Clear aur helpful jawab do."
                }
            ] + user_histories[user_id]
        )

        reply = response.choices[0].message.content

        user_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })

        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error aa gaya! Dobara try karo.\n`{str(e)}`", parse_mode="Markdown")

# ======================== BOT START ========================
print("✅ Shaurya ka bot chal raha hai... 🚀")
bot.polling(none_stop=True)
