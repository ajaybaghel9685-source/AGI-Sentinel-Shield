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
# Yahan apni purani ID rehne dein, niche code ise verify karega
TELEGRAM_CHAT_ID = 9685474533 

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ANGEL_API_KEY = os.environ.get("ANGEL_API_KEY", "").strip()
ANGEL_CLIENT_ID = os.environ.get("ANGEL_CLIENT_ID", "").strip()
ANGEL_PASSWORD = os.environ.get("ANGEL_PASSWORD", "").strip()
ANGEL_TOTP_SECRET = os.environ.get("ANGEL_TOTP_SECRET", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_KEY", "").strip()

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

smartApi = None
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

# ==========================================
# 🛡️ 4. SAFE TELEGRAM SENDER
# ==========================================
def safe_send_message(text):
    try:
        # Hum try karenge aapki hardcoded ID par bhejne ka
        bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode='HTML')
    except:
        logger.error("Could not send automated message. Check Chat ID.")

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
            safe_send_message("🟢 <b>SYSTEM ONLINE:</b> Angel One Login Successful!")
        return True
    except Exception as e:
        logger.error(f"❌ LOGIN FAILED: {e}")
        return False

# ==========================================
# ⚡ 6. TELEGRAM COMMANDS (FIXED)
# ==========================================
@bot.message_handler(commands=['start', 'ping'])
def check_visibility(message):
    # Ye line aapko aapki sahi Chat ID batayegi
    user_id = message.chat.id
    response = f"✅ <b>I CAN SEE YOU!</b>\n\nAapki Chat ID hai: <code>{user_id}</code>\n\nIse code mein TELEGRAM_CHAT_ID ki jagah update karein."
    bot.reply_to(message, response, parse_mode='HTML')

@bot.message_handler(commands=['login'])
def retry_login(message):
    if message.chat.id == TELEGRAM_CHAT_ID:
        bot.reply_to(message, "🔄 Retrying Angel One Login...")
        login_angel_one(silent=False)
    else:
        bot.reply_to(message, f"❌ Unauthorized! ID: {message.chat.id}")

# ==========================================
# 🚀 8. MAIN LOOP
# ==========================================
if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    login_angel_one(silent=True)
    
    logger.info("📡 Starting Telegram Polling...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
