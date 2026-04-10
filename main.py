import os
import telebot
import google.generativeai as genai
# ... baaki purane imports (flask, smartapi) ...

# 🎯 CONFIGURATION
TELEGRAM_CHAT_ID = 6119855904 
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

# Dono tarike se key check karega taaki technical dikkat na aaye
GEMINI_KEY = os.environ.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY")

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY.strip())
        # 'gemini-1.5-flash' zyada fast hai aur error kam deta hai
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Gemini Setup Error: {e}")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.chat.id == TELEGRAM_CHAT_ID:
        user_text = message.text.lower()
        
        # 1. Login Command Check
        if any(word in user_text for word in ["login", "connect", "jodo"]):
            bot.reply_to(message, "Theek hai, Angel One se connect kar raha hoon...")
            # login_angel_one() wala function call hoga
            return

        # 2. AI Chat (Stocks/General Sawal)
        if GEMINI_KEY:
            try:
                # Bot ko instruction ki wo Hindi mein hi jawab de
                prompt = f"Aap ek expert Indian Trading assistant hain. User ne pucha hai: '{message.text}'. Use simple Hindi mein jawab dein."
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text)
            except Exception as e:
                # Agar ab bhi error aaye toh seedha bataiye kya error hai
                bot.reply_to(message, f"❌ AI connect nahi ho raha. Error: {str(e)[:50]}")
        else:
            bot.reply_to(message, "⚠️ Boss, Gemini Key missing hai. Railway Variables check karein!")

# ... (Baaki code polling wala) ...
