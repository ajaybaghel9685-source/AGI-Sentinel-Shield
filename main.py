import os
import telebot
import google.generativeai as genai

# Variables ko Railway se uthane ka sahi tarika
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
# Dono mein se jo bhi mil jaye, usey utha lega
G_KEY = os.environ.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN, threaded=False)

if G_KEY:
    try:
        genai.configure(api_key=G_KEY.strip())
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini AI connect ho gaya hai!")
    except Exception as e:
        print(f"❌ Gemini Setup Error: {e}")

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    if message.chat.id == 6119855904: # Aapki Chat ID
        if G_KEY:
            try:
                # User ka sawal AI ko bhejein
                res = model.generate_content(f"Hindi mein jawab dein: {message.text}")
                bot.reply_to(message, res.text)
            except Exception as e:
                bot.reply_to(message, f"Technical error: {str(e)[:50]}")
        else:
            bot.reply_to(message, "⚠️ Railway mein AI Key nahi mili!")

if __name__ == "__main__":
    print("📡 Bot polling shuru ho rahi hai...")
    bot.infinity_polling(skip_pending=True)
