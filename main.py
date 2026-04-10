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
# 🌐 1. FLASK WEB SERVER (To Satisfy Railway)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Hanuman Matrix Bot is LIVE and running autonomously! 🚀"

def run_web_server():
    """Railway requires an active port to keep the container alive."""
    port = int(os.environ.get("PORT", 8080)) # Railway auto-assigns PORT
    logger.info(f"🌐 Starting Dummy Web Server on port {port}...")
    # use_reloader=False prevents Flask from starting twice in threads
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ==========================================
# 🎯 2. HARDCODED & ENV CONFIGURATION
# ==========================================
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

# ==========================================
# 🤖 3. BOT INITIALIZATION
# ==========================================
try:
    print("⏳ Checking Token...")
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False) # RAM Saver!
    bot_info = bot.get_me()
    print(f"✅ Token Verified! Bot info: {bot_info.first_name} (@{bot_info.username})")
except Exception as e:
    logger.error(f"❌ CRITICAL: Failed to authenticate Bot Token. Error: {e}")
    bot = None

# ==========================================
# 🛡️ 4. SAFE TELEGRAM SENDER
# ==========================================
def safe_send_message(text):
    if not bot:
        return
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"⚠️ Telegram API Error: {e.description}")
    except Exception as e:
        logger.error(f"⚠️ Unknown error while sending message: {e}")

# ==========================================
# 🔐 5. ANGEL ONE LOGIN ENGINE
# ==========================================
def login_angel_one(silent=False):
    global smartApi
    try:
        clean_totp_secret = str(ANGEL_TOTP_SECRET).replace(" ", "").replace("-", "").upper()
        logger.info("⏳ Attempting Angel One Login...")
        
        totp = pyotp.TOTP(clean_totp_secret).now()
        smartApi = SmartConnect(api_key=ANGEL_API_KEY)
        login_response = smartApi.generateSession(ANGEL_CLIENT_ID, ANGEL_PASSWORD, totp)
        
        if login_response.get('status') == False:
            raise Exception(login_response.get('message', 'Unknown API Error'))
            
        logger.info("✅ Angel One Login Successful (In Pool)!")
        
        if not silent:
            safe_send_message("🟢 <b>SYSTEM ONLINE:</b> Angel One Login Successful!")
        return True

    except Exception as e:
        logger.error(f"❌ ANGEL ONE LOGIN FAILED: {str(e)}")
        if not silent:
            safe_send_message(f"❌ <b>LOGIN FAILED:</b> {str(e)}")
        return False

# ==========================================
# ⚡ 6. TELEGRAM COMMANDS
# ==========================================
if bot:
    @bot.message_handler(commands=['start', 'ping'])
    def check_visibility(message):
        if message.chat.id != TELEGRAM_CHAT_ID: return
        bot.reply_to(message, "✅ <b>I CAN SEE YOU BOSS!</b> Connection is Solid.", parse_mode='HTML')

    @bot.message_handler(commands=['login'])
    def retry_login(message):
        if message.chat.id != TELEGRAM_CHAT_ID: return
        bot.reply_to(message, "🔄 Retrying Angel One Login...")
        login_angel_one(silent=False)

# ==========================================
# 🔄 7. KEEP-ALIVE LOGGER
# ==========================================
def keep_alive_logger():
    """Prints a log every 30 seconds to show Railway that the process is active."""
    while True:
        logger.info("⚡ Bot is active and listening for market triggers...")
        time.sleep(30)

# ==========================================
# 🚀 8. KICKSTART & IMMORTALITY LOOP
# ==========================================
if __name__ == "__main__":
    logger.info("⚡ Booting Hanuman Matrix Bot...")

    # A) Start Flask Web Server in a background Daemon Thread
    # Daemon thread ensures it stops when the main program stops
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # B) Start Keep-Alive Logger in background
    logger_thread = threading.Thread(target=keep_alive_logger, daemon=True)
    logger_thread.start()

    # C) Silent Angel One Boot
    login_angel_one(silent=True)
    
    logger.info("📡 Starting Telegram Polling (Infinity Mode)...")
    
    # D) THE IMMORTALITY LOOP
    while True:
        try:
            if bot:
                bot.infinity_polling(timeout=10, long_polling_timeout=5)
            else:
                logger.error("Bot is not initialized. Waiting...")
                time.sleep(30)
        except Exception as e:
            logger.error(f"🚨 Polling Exception: {e}")
            logger.info("🔄 Rebooting polling sequence in 10 seconds...")
            
        time.sleep(10) # CPU Breather         
