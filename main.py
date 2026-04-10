import os
import telebot
import google.generativeai as genai
from flask import Flask
import threading

# 1. Configuration (Railway Variables)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
# Dono mein se jo bhi key Railway mein milegi, ye usey utha lega
AI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY")
MY_CHAT_ID = 6119855904

# 2. Gemini AI Setup
ai_active = False
if AI_KEY:
    try:
        genai.configure(api_key=AI_KEY.strip())
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_active = True
        print("✅ Gemini AI is Ready!")
    except Exception as e:
        print(f"❌ Gemini Setup Error: {e}")

bot = telebot.TeleBot(TOKEN, threaded=False)

# 3. Flask Server (Railway ko active rakhne ke liye)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# 4. Message Handler (Har sawal ka jawab dene ke liye)
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Sirf aapki chat par reply karega
    if message.chat.id == MY_CHAT_ID:
        user_text = message.text
        
        if ai_active:
            try:
                # AI ko instruction ki wo Hindi mein hi jawab de
                prompt = f"User: {user_text}\n\nAssistant: Iska jawab saral Hindi mein trading expert ki tarah dein."
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text)
            except Exception as e:
                # Agar AI fail ho toh error bataye (Technical dikkat nahi)
                bot.reply_to(message, f"⚠️ AI Error: {str(e)[:50]}")
        else:
            bot.reply_to(message, "❌ Key Error: Railway mein GEMINI_API_KEY check karein!")

# 5. Start Execution
if __name__ == "__main__":
    # Flask ko alag thread mein chalayenge
    threading.Thread(target=run_flask).start()
    print("📡 Telegram Polling Started...")
    # skip_pending=True purane atke huye messages ko delete kar dega
    bot.infinity_polling(skip_pending=True)
