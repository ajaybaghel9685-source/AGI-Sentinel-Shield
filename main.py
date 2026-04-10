import os
import time
import pyotp
import telebot
from logzero import logger
from SmartApi import SmartConnect

# ==========================================
# ⚙️ 1. ENVIRONMENT VARIABLES (THE INTEGER FIX)
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

# 🛠️ THE FIX: Stripping hidden spaces and forcing Integer conversion
try:
    TELEGRAM_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID", "0").strip())
except ValueError:
    logger.error("❌ CRITICAL ERROR: TELEGRAM_CHAT_ID is invalid! Please enter numbers only in Railway Variables.")
    TELEGRAM_CHAT_ID = 0

ANGEL_API_KEY = os.environ.get("ANGEL_API_KEY", "").strip()
ANGEL_CLIENT_ID = os.environ.get("ANGEL_CLIENT_ID", "").strip()
ANGEL_PASSWORD = os.environ.get("ANGEL_PASSWORD", "").strip()
ANGEL_TOTP_SECRET = os.environ.get("ANGEL_TOTP_SECRET", "").strip()

# Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ==========================================
# 🛡️ 2. SAFE LOGIN ENGINE
# ==========================================
smartApi = None

def login_angel_one():
    global smartApi
    try:
        # 🧹 TOTP Cleaner
        clean_totp_secret = str(ANGEL_TOTP_SECRET).replace(" ", "").replace("-", "").upper()
        
        logger.info("⏳ Attempting Angel One Login...")
        
        totp = pyotp.TOTP(clean_totp_secret).now()
        smartApi = SmartConnect(api_key=ANGEL_API_KEY)
        login_response = smartApi.generateSession(ANGEL_CLIENT_ID, ANGEL_PASSWORD, totp)
        
        if login_response.get('status') == False:
            raise Exception(login_response.get('message', 'Unknown API Error'))
            
        logger.info("✅ Angel One Login Successful!")
        
        # Ab TELEGRAM_CHAT_ID ek pure Integer hai
        if TELEGRAM_CHAT_ID != 0:
            bot.send_message(TELEGRAM_CHAT_ID, "🟢 <b>SYSTEM ONLINE:</b> Angel One Login Successful!", parse_mode='HTML')
        return True

    except Exception as e:
        error_msg = f"❌ <b>ANGEL ONE LOGIN FAILED!</b>\n\n<b>Reason:</b> {str(e)}\n\nBot is running. Send /login to retry."
        logger.error(error_msg)
        
        if TELEGRAM_CHAT_ID != 0:
            bot.send_message(TELEGRAM_CHAT_ID, error_msg, parse_mode='HTML')
        return False

# ==========================================
# 🤖 3. TELEGRAM COMMANDS
# ==========================================
@bot.message_handler(commands=['start', 'status'])
def send_status(message):
    # Using Integer Comparison now!
    if message.chat.id != TELEGRAM_CHAT_ID: 
        logger.warning(f"Unauthorized access attempt from Chat ID: {message.chat.id}")
        return
    
    status = "🟢 Connected" if smartApi and smartApi.getfeedToken() else "🔴 Disconnected"
    bot.reply_to(message, f"📊 <b>Bot Status:</b> Active\n📈 <b>Angel One:</b> {status}", parse_mode='HTML')

@bot.message_handler(commands=['login'])
def retry_login(message):
    if message.chat.id != TELEGRAM_CHAT_ID: 
        return
    
    bot.reply_to(message, "🔄 Retrying Angel One Login...")
    login_angel_one()

# ==========================================
# 🚀 4. KICKSTART & PERSISTENCE
# ==========================================
if __name__ == "__main__":
    logger.info("⚡ Booting Hanuman Matrix Bot...")
    
    # Auto-login on boot
    login_angel_one()
    
    logger.info("📡 Starting Telegram Polling (Infinity Mode)...")
    # infinity_polling prevents timeout crashes
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
