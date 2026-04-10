import os
import telebot
from SmartApi import SmartConnect
import pyotp
from logzero import logger

# Variables (Railway ke 'Variables' tab se matching)
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
PWD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'login'])
def login_angel(message):
    try:
        # Angel One connection setup
        obj = SmartConnect(api_key=API_KEY)
        token = pyotp.TOTP(TOTP_SECRET).now()
        data = obj.generateSession(CLIENT_ID, PWD, token)
        
        if data['status']:
            bot.reply_to(message, "✅ Jai Hanuman! Angel One Login Successful. Aapka bot ab trading ke liye taiyar hai.")
        else:
            bot.reply_to(message, f"❌ Login Fail: {data['message']}")
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

@bot.message_handler(commands=['status'])
def check_status(message):
    bot.reply_to(message, "🤖 Hanuman-Bot (AGI-Sentinel) Online hai!")

# Is line se bot band nahi hoga
bot.infinity_polling()
