import os
import time
import pyotp
import telebot
from logzero import logger
from SmartApi import SmartConnect

# ==========================================
# âš™ï¸ 1. ENVIRONMENT VARIABLES SETUP
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") # Apna Chat ID dalein taaki error DMs aa sakein

ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ==========================================
# ðŸ›¡ï¸ 2. SAFE LOGIN ENGINE (Crash-Proof)
# ==========================================
smartApi = None

def login_angel_one():
    global smartApi
    try:
        # ðŸ§¹ TOTP Cleaner: Removes spaces & forces uppercase to avoid "Non-base32" error
        clean_totp_secret = str(ANGEL_TOTP_SECRET).replace(" ", "").replace("-", "").upper()
        
        logger.info("â³ Attempting Angel One Login...")
        
        # Generate current TOTP
        totp = pyotp.TOTP(clean_totp_secret).now()
        
        # Connect to SmartAPI
        smartApi = SmartConnect(api_key=ANGEL_API_KEY)
        login_response = smartApi.generateSession(ANGEL_CLIENT_ID, ANGEL_PASSWORD, totp)
        
        if login_response.get('status') == False:
            raise Exception(login_response.get('message', 'Unknown API Error'))
            
        logger.info("âœ… Angel One Login Successful!")
        bot.send_message(TELEGRAM_CHAT_ID, "ðŸŸ¢ <b>SYSTEM ONLINE:</b> Angel One Login Successful!", parse_mode='HTML')
        return True

    except Exception as e:
        error_msg = f"âŒ <b>ANGEL ONE LOGIN FAILED!</b>\n\n<b>Reason:</b> {str(e)}\n\nBot is still running. Send /login to retry."
        logger.error(error_msg)
        bot.send_message(TELEGRAM_CHAT_ID, error_msg, parse_mode='HTML')
        return False

# ==========================================
# ðŸ¤– 3. TELEGRAM COMMANDS
# ==========================================
@bot.message_handler(commands=['start', 'status'])
def send_status(message):
    if str(message.chat.id) != TELEGRAM_CHAT_ID: return
    
    status = "ðŸŸ¢ Connected" if smartApi and smartApi.getfeedToken() else "ðŸ”´ Disconnected"
    bot.reply_to(message, f"ðŸ“Š <b>Bot Status:</b> Active\nðŸ“ˆ <b>Angel One:</b> {status}", parse_mode='HTML')

@bot.message_handler(commands=['login'])
def retry_login(message):
    if str(message.chat.id) != TELEGRAM_CHAT_ID: return
    
    bot.reply_to(message, "ðŸ”„ Retrying Angel One Login...")
    login_angel_one()

# ==========================================
# ðŸš€ 4. KICKSTART & PERSISTENCE
# ==========================================
if __name__ == "__main__":
    logger.info("âš¡ Booting Hanuman Matrix Bot...")
    
    # Pehli baar run par automatically login try karega
    login_angel_one()
    
    logger.info("ðŸ“¡ Starting Telegram Polling (Infinity Mode)...")
    # infinity_polling Ensures bot never dies even if Telegram servers hiccup
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
