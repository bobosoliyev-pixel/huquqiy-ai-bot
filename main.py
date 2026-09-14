import os
import time
import requests
import telebot
from telebot import types


# ==============================
# SOZLAMALAR
# ==============================

BOT_TOKEN = os.getenv("8162119640:AAE8cd0GKNyXlTM1KK6Cm7VayjvC_dC6i5s")
OPENAI_API_KEY = os.getenv("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")

ADMIN_ID = 7180429594

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN sozlanmagan!")

bot = telebot.TeleBot(BOT_TOKEN)

users = set()
broadcast_mode = set()


# ==============================
# ASOSIY MENYU
# ==============================

def main_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        "🤖 AI bilan suhbat",
        "⚖️ Huquqiy maslahat"
    )

    markup.add(
        "📚 Qonunlar",
        "🔎 Qidirish"
    )

    markup.add(
        "📝 Savol berish",
        "ℹ️ Bot haqida"
    )

    markup.add(
        "☎️ Foydali ma'lumot"
    )

    return markup


# ==============================
# ADMIN MENYU
# ==============================

def admin_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        "👥 Foydalanuvchilar",
        "📊 Statistika"
    )

    markup.add(
        "📢 Xabar yuborish"
    )

    markup.add(
        "🏠 Asosiy menyu"
    )

    return markup


# ==============================
# AI
# ==============================

def ask_ai(question):

    if not OPENAI_API_KEY:
        return "❌ AI sozlanmagan."

    url = "https://api.openai.com/v1/responses"

    headers = {
        "Authorization": "Bearer " + OPENAI_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-5.6-luna",
        "instructions": (
            "Sen O'zbekiston qonunchiligi bo'yicha "
            "umumiy ma'lumot beruvchi AI yordamchisan. "
            "Doimo o'zbek tilida javob ber. "
            "Javoblarni tushunarli va foydali yoz. "
            "Mavzuga mos emoji va smayliklardan me'yorida foydalan. "
            "Masalan: ⚖️ 📚 📌 💡 ⚠️. "
            "Qonun moddasi raqami aniq bo'lmasa, o'ylab topma. "
            "Kerak bo'lsa LexUZ rasmiy manbasini tekshirishni tavsiya qil. "
            "Qonunni buzish yoki chetlab o'tish bo'yicha yordam bermagin. "
            "Bu umumiy huquqiy ma'lumot ekanini hisobga ol."
        ),
        "input": question
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        if response.status_code != 200:

            print("OPENAI ERROR:")
            print(response.status_code)
            print(response.text)

            return (
                "❌ AI bilan bog'lanishda xatolik yuz berdi.\n\n"
                "⏳ Birozdan keyin qayta urinib ko'ring."
            )

        result = response.json()

        answer = result.get("output_text")

        if answer:
            return answer.strip()

        output = result.get("output", [])

        for item in output:

            content = item.get("content", [])

            for part in content:

                if part.get("type") == "output_text":

                    text = part.get("text")

                    if text:
                        return text.strip()

        return "❌ AI javobini olishda xatolik."

    except requests.exceptions.Timeout:

        return (
            "⏳ AI javobi kechikdi.\n"
            "🔄 Qaytadan urinib ko'ring."
        )

    except Exception as error:

        print("AI ERROR:", error)

        return (
            "❌ Texnik xatolik yuz berdi.\n"
            "🔄 Keyinroq qayta urinib ko'ring."
        )


# ==============================
# START
# ==============================

@bot.message_handler(commands=["start"])
def start(message):

    users.add(message.from_user.id)

    bot.send_message(
        message.chat.id,
        "⚖️ <b>Huquqiy AI botga xush kelibsiz!</b>\n\n"
        "🇺🇿 O'zbekiston qonunchiligi bo'yicha "
        "umumiy ma'lumot olishga yordam beraman.\n\n"
        "👇 Kerakli bo'limni tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# ==============================
# MY ID
# ==============================

@bot.message_handler(commands=["myid"])
def myid(message):

    bot.send_message(
        message.chat.id,
        "🆔 Sizning Telegram ID'ingiz:\n\n"
        f"<code>{message.from_user.id}</code>",
        parse_mode="HTML"
    )


# ==============================
# ADMIN
# ==============================

@bot.message_handler(commands=["admin"])
def admin(message):

    users.add(message.from_user.id)

    if message.from_user.id != ADMIN_ID:

        bot.send_message(
            message.chat.id,
            "❌ Siz admin emassiz."
        )

        return

    bot.send_message(
        message.chat.id,
        "👨‍💻 <b>Admin panel</b>\n\n"
        "👇 Kerakli bo'limni tanlang:",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )


# ==============================
# BARCHA MATN XABARLAR
# ==============================

@bot.message_handler(content_types=["text"])
def handle_text(message):

    user_id = message.from_user.id
    text = message.text.strip()

    users.add(user_id)


    # ==========================
    # ADMIN XABAR YUBORISH
    # ==========================

    if user_id == ADMIN_ID and user_id in broadcast_mode:

        if text == "🏠 Asosiy menyu":

            broadcast_mode.discard(user_id)

            bot.send_message(
                user_id,
                "🏠 Asosiy menyu:",
                reply_markup=main_menu()
            )

            return

        broadcast_mode.discard(user_id)

        success = 0
        failed = 0

        for chat_id in list(users):

            try:

                bot.send_message(
                    chat_id,
                    "📢 <b>Admin xabari</b>\n\n" + text,
                    parse_mode="HTML"
                )

                success += 1

            except Exception as error:

                print("BROADCAST ERROR:", error)
                failed += 1

        bot.send_message(
            user_id,
            "✅ <b>Xabar yuborildi!</b>\n\n"
            f"📨 Yetkazildi: {success}\n"
            f"❌ Yetkazilmadi: {failed}",
            parse_mode="HTML",
            reply_markup=admin_menu()
        )

        return


    # ==========================
    # FOYDALANUVCHILAR
    # ==========================

    if text == "👥 Foydalanuvchilar":

        if user_id != ADMIN_ID:
            return

        bot.send_message(
            user_id,
            "👥 <b>Foydalanuvchilar</b>\n\n"
            f"📊 Jami: {len(users)}",
            parse_mode="HTML"
        )

        return


    # ==========================
    # STATISTIKA
    # ==========================

    if text == "📊 Statistika":

        if user_id != ADMIN_ID:
            return

        bot.send_message(
            user_id,
            "📊 <b>Statistika</b>\n\n"
            f"👥 Foydalanuvchilar: {len(users)}\n"
            "🤖 AI: faol",
            parse_mode="HTML"
        )

        return


    # ==========================
    # XABAR YUBORISH
    # ==========================

    if text == "📢 Xabar yuborish":

        if user_id != ADMIN_ID:
            return

        broadcast_mode.add(user_id)

        bot.send_message(
            user_id,
            "📢 <b>Xabar yuborish</b>\n\n"
            "Barcha foydalanuvchilarga yubormoqchi "
            "bo'lgan xabaringizni yozing.\n\n"
            "🏠 Bekor qilish uchun "
            "«Asosiy menyu»ni bosing.",
            parse_mode="HTML"
        )

        return


    # ==========================
    # ASOSIY MENYU
    # ==========================

    if text == "🏠 Asosiy menyu":

        bot.send_message(
            user_id,
            "🏠 <b>Asosiy menyu</b>\n\n"
            "👇 Kerakli bo'limni tanlang:",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

        return


    # ==========================
    # AI BILAN SUHBAT
    # ==========================

    if text == "🤖 AI bilan suhbat":

        bot.send_message(
            user_id,
            "🤖 <b>AI bilan suhbat</b>\n\n"
            "Savolingizni yozing. 😊\n\n"
            "💡 Masalan:\n"
            "• 16 yoshda ishlash mumkinmi?\n"
            "• Shartnoma nima?\n"
            "• Voyaga yetmaganlarning huquqlari qanday?",
            parse_mode="HTML"
        )

        return


    # ==========================
    # HUQUQIY MASLAHAT
    # ==========================

    if text == "⚖️ Huquqiy maslahat":

        bot.send_message(
            user_id,
            "⚖️ <b>Huquqiy maslahat</b>\n\n"
            "Huquqiy savolingizni yozing. 📚",
            parse_mode="HTML"
        )

        return


    # ==========================
    # QONUNLAR
    # ==========================

    if text == "📚 Qonunlar":

        bot.send_message(
            user_id,
            "📚 <b>Huquqiy yo'nalishlar</b>\n\n"
            "🇺🇿 Konstitutsiya\n"
            "⚒️ Mehnat huquqi\n"
            "👨‍👩‍👧 Oila huquqi\n"
            "🏠 Fuqarolik huquqi\n"
            "⚖️ Ma'muriy huquq\n"
            "📖 Jinoyat huquqi\n\n"
            "💡 Mavzuni yozing, AI tushuntirib beradi.",
            parse_mode="HTML"
        )

        return


    # ==========================
    # QIDIRISH
    # ==========================

    if text == "🔎 Qidirish":

        bot.send_message(
            user_id,
            "🔎 <b>Qidirish</b>\n\n"
            "Qidirayotgan huquqiy mavzuni yozing. 📚",
            parse_mode="HTML"
        )

        return


    # ==========================
    # SAVOL BERISH
    # ==========================

    if text == "📝 Savol berish":

        bot.send_message(
            user_id,
            "📝 <b>Savolingizni yozing.</b>\n\n"
            "Oddiy tilda yozishingiz mumkin. 😊",
            parse_mode="HTML"
        )

        return


    # ==========================
    # BOT HAQIDA
    # ==========================

    if text == "ℹ️ Bot haqida":

        bot.send_message(
            user_id,
            "ℹ️ <b>Huquqiy AI bot</b>\n\n"
            "🤖 Huquqiy savollarga umumiy ma'lumot "
            "berishga yordam beradi.\n\n"
            "🇺🇿 Asosiy yo'nalish: O'zbekiston qonunchiligi.\n\n"
            "⚠️ Javoblar professional yuridik "
            "maslahat o'rnini bosmaydi.",
            parse_mode="HTML"
        )

        return


    # ==========================
    # FOYDALI MA'LUMOT
    # ==========================

    if text == "☎️ Foydali ma'lumot":

        bot.send_message(
            user_id,
            "☎️ <b>Foydali ma'lumot</b>\n\n"
            "📚 Huquqiy masalalarda rasmiy "
            "manbalardan foydalanish tavsiya etiladi.\n\n"
            "💡 Savolingizni yozing.",
            parse_mode="HTML"
        )

        return


    # ==========================
    # ODDIY MATN → AI
    # ==========================

    bot.send_chat_action(
        user_id,
        "typing"
    )

    answer = ask_ai(text)

    bot.send_message(
        user_id,
        answer
    )


# ==============================
# BOTNI ISHGA TUSHIRISH
# ==============================

if __name__ == "__main__":

    print("🤖 Bot ishga tushdi...")

    while True:

        try:

            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )

        except Exception as error:

            print("BOT ERROR:", error)

            time.sleep(5)
