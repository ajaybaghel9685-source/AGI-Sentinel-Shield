import os
import time
import pyotp
import telebot
from logzero import logger
from SmartApi import SmartConnect

# Safe Gemini Import
import google.generativeai as genai

# ==========================================
# 🎯 1. HARDCODED & ENV CONFIGURATION
# ==========================================
TELEGRAM_CHAT_ID = 9685474533

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ANGEL_API_KEY = os.environ.get("ANGEL_API_KEY", "").strip()
ANGEL_CLIENT_ID = os.environ.get("ANGEL_CLIENT_ID", "").strip()
ANGEL_PASSWORD = os.environ.get("ANGEL_PASSWORD", "").strip()
ANGEL_TOTP_SECRET = os.environ.get("ANGEL_TOTP_SECRET", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_KEY", "").strip()

# Initialize Telegram Bot (No crashing if token is empty during build phase)
try:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
except Exception as e:
    logger.error(f"Failed to initialize Bot: {e}")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

smartApi = None

# ==========================================
# 🛡️ 2. SAFE TELEGRAM SENDER
# ==========================================
def safe_send_message(text):
    try:
        if bot:
            bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"⚠️ Telegram API Error: {e}")

# ==========================================
# 🔐 3. ANGEL ONE LOGIN ENGINE
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
# 🤖 4. TELEGRAM COMMANDS
# ==========================================
@bot.message_handler(commands=['start', 'ping'])
def check_visibility(message):
    if message.chat.id != TELEGRAM_CHAT_ID: 
        return
    bot.reply_to(message, "✅ <b>I CAN SEE YOU BOSS!</b> Immortality Protocol Active.", parse_mode='HTML')

@bot.message_handler(commands=['login'])
def retry_login(message):
    if message.chat.id != TELEGRAM_CHAT_ID: return
    bot.reply_to(message, "🔄 Retrying Angel One Login...")
    login_angel_one(silent=False)

# ==========================================
# 🚀 5. KICKSTART & IMMORTALITY LOOP
# ==========================================
if __name__ == "__main__":
    logger.info("⚡ Booting Hanuman Matrix Bot...")
    
    # 1. Silent Boot
    login_angel_one(silent=True)
    
    logger.info("📡 Starting Telegram Polling (Infinity Mode)...")
    
    # 2. THE IMMORTALITY LOOP (Railway Anti-Stop Mechanism)
    while True:
        try:
            # infinity_polling will block execution here as long as it's running
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"🚨 Polling Crashed (Network Glitch?): {e}")
            logger.info("🔄 Rebooting polling sequence in 10 seconds to keep container alive...")
            
        # 3. CPU Breather: Ensure container doesn't get killed for maxing CPU if loop runs wild
        time.sleep(10)
