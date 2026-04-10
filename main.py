import os
import time
import pyotp
import telebot
import threading
from logzero import logger
from flask import Flask
from SmartApi import SmartConnect
import google.generativeai as genai

# ==========================================
# 🌐 1. FLASK WEB SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Hanuman Matrix Bot is LIVE! 🚀"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ==========================================
# 🎯 2. CONFIGURATION
# ==========================================
TELEGRAM_CHAT_ID = 6119855904 # Aapki sahi ID

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ANGEL_API_KEY = os.environ.get("ANGEL_API_KEY", "").strip()
ANGEL_CLIENT_ID = os.environ.get("ANGEL_CLIENT_ID", "").strip()
ANGEL_PASSWORD = os.environ.get("ANGEL_PASSWORD", "").strip()
ANGEL_TOTP_SECRET = os.environ.get("ANGEL_TOTP_SECRET", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_KEY", "").strip()

# Gemini Setup
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')

smartApi = None
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

# ==========================================
# 🛡️ 4. SAFE TELEGRAM SENDER
# ==========================================
def safe_send_message(text):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Telegram error: {e}")

# ==========================================
# 🔐 5. ANGEL ONE LOGIN
# ==========================================
def login_angel_one(silent=False):
    global smartApi
    try:
        clean_totp_secret = str(ANGEL_TOTP_SECRET).replace(" ", "").upper()
        totp = pyotp.TOTP(clean_totp_secret).now()
        smartApi = SmartConnect(api_key=ANGEL_API_KEY)
        login_response = smartApi.generateSession(ANGEL_CLIENT_ID, ANGEL_PASSWORD, totp)
        
        if login_response.get('status') == False:
            raise Exception(login_response.get('message', 'Login Error'))
            
        logger.info("✅ Angel One Login Successful!")
        if not silent:
            safe_send_message("🟢 <b>SYSTEM ONLINE:</b> Angel One Login Ho Gaya Hai!")
        return True
    except Exception as e:
        logger.error(f"❌ LOGIN FAILED: {e}")
        return False

# ==========================================
# ⚡ 6. HINDI AI & COMMAND HANDLING
# ==========================================

@bot.message_handler(func=lambda message: True)
def handle_hindi_ai(message):
    # Sirf aapki ID se baat karega
    if message.chat.id != TELEGRAM_CHAT_ID:
        return

    user_text = message.text.lower()

    # 1. Trading Commands (Hindi Keywords)
    if any(word in user_text for word in ["login", "jodo", "connect", "shuru karo"]):
        bot.reply_to(message, "Theek hai, Angel One se connect kar raha hoon...")
        login_angel_one()

    elif any(word in user_text for word in ["status", "kaise ho", "chal raha hai"]):
        bot.reply_to(message, "System ekdum mast chal raha hai, Boss! Market par nazar hai. 🚀")

    elif any(word in user_text for word in ["ping", "zinda ho"]):
        bot.reply_to(message, "✅ Ji Boss! I CAN SEE YOU!")

    # 2. General AI Chat (Gemini)
    else:
        try:
            if GEMINI_KEY:
                # Bot ko instruction ki wo Hindi mein hi jawab de
                prompt = f"User says: {message.text}. Respond as a helpful trading assistant in simple Hindi."
                response = model.generate_content(prompt)
                bot.reply_to(message, response.text)
            else:
                bot.reply_to(message, "Aapka message mila, par AI key nahi hai isliye main sirf trading commands samajh sakta hoon.")
        except Exception as e:
            bot.reply_to(message, "Maaf kijiyega, kuch technical dikkat aa gayi hai.")

# ==========================================
# 🚀 8. MAIN LOOP
# ==========================================
if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    login_angel_one(silent=True)
    
    logger.info("📡 Starting Telegram Polling...")
    # Infinity polling with skip_pending to avoid 409 conflict
    bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
