import os
import time
import pyotp
import telebot
from logzero import logger
from SmartApi import SmartConnect

# Safe Gemini Import (Won't leak memory)
import google.generativeai as genai

# ==========================================
# 🎯 1. HARDCODED CONFIGURATION
# ==========================================
# User Command: Hardcode the exact integer Chat ID
TELEGRAM_CHAT_ID = 9685474533

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ANGEL_API_KEY = os.environ.get("ANGEL_API_KEY", "").strip()
ANGEL_CLIENT_ID = os.environ.get("ANGEL_CLIENT_ID", "").strip()
ANGEL_PASSWORD = os.environ.get("ANGEL_PASSWORD", "").strip()
ANGEL_TOTP_SECRET = os.environ.get("ANGEL_TOTP_SECRET", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_KEY", "").strip()

# Initialize Telegram Bot & AI
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

smartApi = None

# ==========================================
# 🛡️ 2. SAFE TELEGRAM SENDER (Crash-Proof)
# ==========================================
def safe_send_message(text):
    """Ye function make sure karega ki agar chat not found ho, toh code crash na ho."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"⚠️ Telegram API Error: {e}")
        logger.warning("Did you forget to send /start to your bot in the Telegram App?")

# ==========================================
# 🔐 3. ANGEL ONE LOGIN ENGINE (Silent Mode)
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
        
        # 🤫 Silent Start: Boot par message nahi bhejega, crash se bachega!
        if not silent:
            safe_send_message("🟢 <b>SYSTEM ONLINE:</b> Angel One Login Successful!")
        return True

    except Exception as e:
        logger.error(f"❌ ANGEL ONE LOGIN FAILED: {str(e)}")
        if not silent:
            safe_send_message(f"❌ <b>LOGIN FAILED:</b> {str(e)}")
        return False

# ==========================================
# 🤖 4. TELEGRAM COMMANDS (Validation)
# ==========================================
@bot.message_handler(commands=['start', 'ping'])
def check_visibility(message):
    """Validation: Checking if the bot can 'see' you."""
    if message.chat.id != TELEGRAM_CHAT_ID: 
        logger.warning(f"Unauthorized ID tried to connect: {message.chat.id}")
        return
    
    bot.reply_to(message, "✅ <b>I CAN SEE YOU BOSS!</b> Connection is verified and solid.", parse_mode='HTML')

@bot.message_handler(commands=['login'])
def retry_login(message):
    if message.chat.id != TELEGRAM_CHAT_ID: return
    
    bot.reply_to(message, "🔄 Manual Login Triggered. Connecting to Angel One...")
    login_angel_one(silent=False) # Ab user ne request ki hai, toh silent=False

# ==========================================
# 🚀 5. KICKSTART & PERSISTENCE
# ==========================================
if __name__ == "__main__":
    logger.info("⚡ Booting Hanuman Matrix Bot...")
    
    # SILENT START: Boot par API hit nahi karega Telegram ko
    login_angel_one(silent=True)
    
    logger.info("📡 Starting Telegram Polling (Infinity Mode)...")
    # Ye process ko block karke rakhega taaki container band na ho
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
