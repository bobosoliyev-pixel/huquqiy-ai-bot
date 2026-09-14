import os
import requests
import telebot
from telebot import types

# =========================
# SOZLAMALAR
# =========================

BOT_TOKEN = os.getenv("8162119640:AAE8cd0GKNyXlTM1KK6Cm7VayjvC_dC6i5s")
OPENAI_API_KEY = os.getenv("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")

ADMIN_ID = 7180429594

bot = telebot.TeleBot(BOT_TOKEN)


# =========================
# /start
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    ai_button = types.KeyboardButton("🤖 AI bilan suhbat")
    about_button = types.KeyboardButton("ℹ️ Bot haqida")
    admin_button = types.KeyboardButton("👨‍💻 Admin")

    keyboard.add(ai_button)
    keyboard.add(about_button, admin_button)

    bot.send_message(
        message.chat.id,
        f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
        "Men AI bilan ishlaydigan Telegram botman. 🤖\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=keyboard
    )


# =========================
# AI BILAN SUHBAT
# =========================

@bot.message_handler(func=lambda message: message.text == "🤖 AI bilan suhbat")
def ai_start(message):
    bot.send_message(
        message.chat.id,
        "🤖 Savolingizni yozing.\n\n"
        "Men AI yordamida javob beraman."
    )


# =========================
# BOT HAQIDA
# =========================

@bot.message_handler(func=lambda message: message.text == "ℹ️ Bot haqida")
def about(message):
    bot.send_message(
        message.chat.id,
        "🤖 Bu Telegram AI bot.\n\n"
        "Bot sun’iy intellekt yordamida savollarga javob beradi.\n"
        "Savolingizni oddiy qilib yozishingiz mumkin."
    )


# =========================
# ADMIN
# =========================

@bot.message_handler(func=lambda message: message.text == "👨‍💻 Admin")
def admin(message):
    bot.send_message(
        message.chat.id,
        "👨‍💻 Admin bilan bog‘lanish uchun:\n"
        "Telegram orqali murojaat qiling."
    )


# =========================
# /admin
# =========================

@bot.message_handler(commands=["admin"])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "❌ Sizda admin huquqi yo‘q."
        )
        return

    bot.send_message(
        message.chat.id,
        "✅ Siz adminsiz.\n\n"
        "Bot ishlamoqda."
    )


# =========================
# AI SO‘ROV
# =========================

def ask_ai(question):
    if not OPENAI_API_KEY:
        return "❌ OPENAI_API_KEY sozlanmagan."

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sen foydalanuvchiga o‘zbek tilida yordam beradigan "
                    "AI assistantsan. Javoblarni tushunarli, qisqa va foydali ber."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        if response.status_code != 200:
            return "❌ AI bilan bog‘lanishda xatolik yuz berdi."

        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception:
        return "❌ Xatolik yuz berdi. Keyinroq qayta urinib ko‘ring."


# =========================
# ODDIY MATN XABARLARI
# =========================

@bot.message_handler(content_types=["text"])
def handle_text(message):

    # Tugmalar alohida handlerlarda ishlaydi
    if message.text in [
        "🤖 AI bilan suhbat",
        "ℹ️ Bot haqida",
        "👨‍💻 Admin"
    ]:
        return

    bot.send_chat_action(
        message.chat.id,
        "typing"
    )

    answer = ask_ai(message.text)

    bot.send_message(
        message.chat.id,
        answer
    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":
    print("Bot ishga tushdi...")

    bot.infinity_polling(
        skip_pending=True
    )
