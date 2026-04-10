import os
import telebot
from SmartApi import SmartConnect
import pyotp
from logzero import logger

# Variables (Railway se uthayega)
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
PWD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
obj = SmartConnect(api_key=API_KEY)

@bot.message_handler(commands=['start', 'login'])
def login_angel(message):
    try:
        token = pyotp.TOTP(TOTP_SECRET).now()
        data = obj.generateSession(CLIENT_ID, PWD, token)
        if data['status']:
            bot.reply_to(message, "✅ Angel One Login Successful! Bot ab active hai.")
        else:
            bot.reply_to(message, f"❌ Login Fail: {data['message']}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

@bot.message_handler(commands=['status'])
def check_status(message):
    bot.reply_to(message, "🤖 Hanuman-Bot chalu hai aur Angel One se connect hone ko taiyar hai.")

bot.infinity_polling()
