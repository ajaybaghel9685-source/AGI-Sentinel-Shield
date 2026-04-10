import os
import telebot
import google.generativeai as genai

# Railway Variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
# Jo bhi key mile, use utha lo
G_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY")
MY_ID = 6119855904

bot = telebot.TeleBot(TOKEN, threaded=False)

# AI Setup check
if G_KEY:
    try:
        genai.configure(api_key=G_KEY.strip())
        # Model ka ekdum sahi naam
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini Ready!")
    except Exception as e:
        print(f"❌ Gemini Error: {e}")

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    if message.chat.id == MY_ID:
        # Agar AI key hai toh jawab do
        if G_KEY:
            try:
                # Direct simple response
                res = model.generate_content(f"Hindi: {message.text}")
                bot.reply_to(message, res.text)
            except Exception as e:
                # Agar Gemini fail ho toh error bataye (Technical dikkat nahi)
                bot.reply_to(message, f"⚠️ AI Connection Error: {str(e)[:40]}")
        else:
            bot.reply_to(message, "❌ Railway mein GEMINI_KEY missing hai!")

if __name__ == "__main__":
    print("📡 Bot is starting...")
    bot.infinity_polling(skip_pending=True)
