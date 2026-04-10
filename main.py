import os
import telebot
import google.generativeai as genai
from flask import Flask
import threading

# 1. Configuration - Railway Variables se data uthayega
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
# Aapne GEMINI_KEY set kiya hai, code ise hi dhundhega
G_KEY = os.environ.get("GEMINI_KEY")
MY_CHAT_ID = 6119855904

# 2. Gemini AI Setup
if G_KEY:
    try:
        genai.configure(api_key=G_KEY.strip())
        # Fast model use kar rahe hain taaki turant jawab mile
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Gemini Error: {e}")

bot = telebot.TeleBot(TOKEN, threaded=False)

# 3. Flask Server (Railway ko "Active" rakhne ke liye zaroori hai)
app = Flask(__name__)
@app.route('/')
def index(): return "Bot is Online!"

def run_server():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# 4. Message Handler (Har sawal ka jawab dene ke liye)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # Sirf aapki Chat ID par reply karega (Security ke liye)
    if message.chat.id == MY_CHAT_ID:
        user_input = message.text
        
        # "Ok" likhne par bolne wala system (Future update ke liye placeholder)
        if user_input.lower() == "ok":
            bot.reply_to(message, "Theek hai bhai, ab main bol kar bhi jawab de sakta hoon (Ready).")
            return

        try:
            # AI ko instruction: Hindi mein aur trading expert ki tarah jawab de
            instruction = f"Aap ek expert Indian assistant hain. User ka sawal: {user_input}. Iska jawab saral Hindi mein dein."
            response = model.generate_content(instruction)
            bot.reply_to(message, response.text)
        except Exception as e:
            bot.reply_to(message, "Maaf kijiyega, abhi AI connect nahi ho pa raha. Ek baar Railway mein Key check karein.")
            print(f"Chat Error: {e}")

# 5. Execution
if __name__ == "__main__":
    # Flask ko alag thread mein chalayenge
    threading.Thread(target=run_server).start()
    print("📡 Bot is starting... Polling active.")
    # skip_pending=True se purane atke huye messages ignore ho jayenge
    bot.infinity_polling(skip_pending=True)
