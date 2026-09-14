import os
import requests
import telebot
from telebot import types
from dotenv import load_dotenv

# .env fayldan sozlamalarni o'qish
load_dotenv()

# =========================
# SOZLAMALAR
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ .env faylida BOT_TOKEN va OPENAI_API_KEY sozlanishi shart!")

bot = telebot.TeleBot(BOT_TOKEN)

# User suhbatlari tarixini saqlash
user_conversations = {}


# =========================
# /start
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user_conversations[user_id] = []  # Suhbat tarixini boshlaymiz
    
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
        "Kerakli bo'limni tanlang:",
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
        "Bot sun'iy intellekt yordamida savollarga javob beradi.\n"
        "Savolingizni oddiy qilib yozishingiz mumkin."
    )


# =========================
# ADMIN
# =========================

@bot.message_handler(func=lambda message: message.text == "👨‍💻 Admin")
def admin(message):
    bot.send_message(
        message.chat.id,
        "👨‍💻 Admin bilan bog'lanish uchun:\n"
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
            "❌ Sizda admin huquqi yo'q."
        )
        return

    bot.send_message(
        message.chat.id,
        "✅ Siz adminsiz.\n\n"
        "Bot ishlamoqda."
    )


# =========================
# AI SO'ROV (CONTEXT BILAN)
# =========================

def ask_ai(user_id, question):
    """OpenAI APIga so'rov yuborish (suhbat tarixini saqlash bilan)"""
    
    if not OPENAI_API_KEY:
        return "❌ OPENAI_API_KEY sozlanmagan."

    if not question.strip():
        return "⚠️ Iltimos, savolingizni to'liq yozing."

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Suhbat tarixini o'qish
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    messages = [
        {
            "role": "system",
            "content": (
                "Sen foydalanuvchiga o'zbek tilida yordam beradigan "
                "AI assistantsan. Javoblarni tushunarli, qisqa va foydali ber."
            )
        }
    ]

    # Oldingi suhbatlarni qo'shamiz
    messages.extend(user_conversations[user_id])

    # Yangi savolni qo'shamiz
    messages.append({"role": "user", "content": question})

    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        if response.status_code != 200:
            error_info = response.json().get("error", {})
            return f"❌ Xatolik: {error_info.get('message', 'Noma\'lum xatolik')}"

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        # Suhbat tarixiga qo'shamiz
        user_conversations[user_id].append({"role": "user", "content": question})
        user_conversations[user_id].append({"role": "assistant", "content": answer})

        # Tarixni 10 ta oxirgi xabar bilan cheklash (tokenlarni tejash uchun)
        if len(user_conversations[user_id]) > 20:
            user_conversations[user_id] = user_conversations[user_id][-20:]

        return answer

    except requests.exceptions.Timeout:
        return "⏱️ Vaqt tugadi. Keyinroq qayta urinib ko'ring."
    except requests.exceptions.RequestException as e:
        return f"❌ Xatolik: {str(e)}"
    except Exception as e:
        return f"❌ Noma'lum xatolik: {str(e)}"


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

    user_id = message.from_user.id
    
    bot.send_chat_action(
        message.chat.id,
        "typing"
    )

    answer = ask_ai(user_id, message.text)

    bot.send_message(
        message.chat.id,
        answer
    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    print("✅ Bot tayyorlandi va buklashni kutmoqda...")

    try:
        bot.infinity_polling(
            skip_pending=True
        )
    except KeyboardInterrupt:
        print("\n❌ Bot to'xtadi.")
    except Exception as e:
        print(f"❌ Xatolik: {e}")
