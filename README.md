# 🤖 Huquqiy AI Bot

Telegram bo'tida AI yordamida savollarga javob beradigan bot.

## 🚀 O'rnatish

### 1. Kerakli kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. .env faylini sozlash
```bash
cp .env.example .env
```

`.env` faylni o'chirib qo'ying va kerakli qiymatlarni kiriting:
```env
BOT_TOKEN=your_new_bot_token
OPENAI_API_KEY=your_new_openai_api_key
ADMIN_ID=your_admin_id
```

### 3. Botni ishga tushirish
```bash
python bot.py
```

## 📝 Xususiyatlar

✅ **AI bilan suhbat** - OpenAI GPT-4o-mini orqali  
✅ **Suhbat tarixini saqlash** - Context-ni eslab qoladi  
✅ **O'zbek tilida** - Foydalanuvchi uchun qulay  
✅ **Admin paneli** - Faqat admin uchun  
✅ **Xavfli sozlamalar** - .env orqali  

## 🔒 Xavfsizlik

❌ Hech qachon API kalitlarni kodga yozmang!  
✅ Har doim `.env` fayldan o'qing  
✅ `.env` faylni `.gitignore` ga qo'shish shart!  
✅ Eski kalitlarni disable qiling!  

## 📞 Admin Kommandalar

- `/start` - Botni ishga tushirish
- `/admin` - Admin statusini tekshirish

## 📄 Litsenziya

MIT License
