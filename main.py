import os
import time
import pyotp
import telebot
from logzero import logger
from SmartApi import SmartConnect
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

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

smartApi = None

# ==========================================
# 🤖 2. BOT INITIALIZATION & VERIFICATION
# ==========================================
try:
    print("⏳ Checking Token...")
    # FIX 1: threaded=False to prevent conflicts on Railway's small containers
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
    
    # FIX 3: Verify if the new token is actually working
    bot_info = bot.get_me()
    print(f"✅ Token Verified! Bot info: {bot_info.first_name} (@{bot_info.username})")
except Exception as e:
    logger.error(f"❌ CRITICAL: Failed to authenticate Bot Token. Check your TELEGRAM_BOT_TOKEN. Error: {e}")
    # We don't exit here so the container stays alive to show the log.
    bot = None

# ==========================================
# 🛡️ 3. SAFE TELEGRAM SENDER
# ==========================================
def safe_send_message(text):
    if not bot:
        return
    # FIX 2: try-except block around send_message to prevent crashes
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"⚠️ Telegram API Error (Code: {e.error_code}): {e.description}")
        logger.warning(f"Failed to send message to Chat ID: {TELEGRAM_CHAT_ID}. Please send /start to the bot.")
    except Exception as e:
        logger.error(f"⚠️ Unknown error while sending message: {e}")

# ==========================================
# 🔐 4. ANGEL ONE LOGIN ENGINE
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
# ⚡ 5. TELEGRAM COMMANDS
# ==========================================
# We must ensure 'bot' exists before registering handlers
if bot:
    @bot.message_handler(commands=['start', 'ping'])
    def check_visibility(message):
        if message.chat.id != TELEGRAM_CHAT_ID: 
            return
        bot.reply_to(message, "✅ <b>I CAN SEE YOU BOSS!</b> Connection is Solid.", parse_mode='HTML')

    @bot.message_handler(commands=['login'])
    def retry_login(message):
        if message.chat.id != TELEGRAM_CHAT_ID: return
        bot.reply_to(message, "🔄 Retrying Angel One Login...")
        login_angel_one(silent=False)

# ==========================================
# 🚀 6. KICKSTART & IMMORTALITY LOOP
# ==========================================
if __name__ == "__main__":
    logger.info("⚡ Booting Hanuman Matrix Bot...")
    
    # Silent Boot
    login_angel_one(silent=True)
    
    logger.info("📡 Starting Telegram Polling (Infinity Mode)...")
    
    # IMMORTALITY LOOP
    while True:
        try:
            if bot:
                # infinity_polling works even with threaded=False
                bot.infinity_polling(timeout=10, long_polling_timeout=5)
            else:
                logger.error("Bot is not initialized. Cannot start polling.")
                time.sleep(30) # Wait longer if token is entirely invalid
        except Exception as e:
            logger.error(f"🚨 Polling Exception: {e}")
            logger.info("🔄 Rebooting polling sequence in 10 seconds...")
            
        # CPU Breather
        time.sleep(10)
