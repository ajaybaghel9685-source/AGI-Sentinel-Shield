import os
import telebot
from smartapi import SmartConnect
import pyotp
from logzero import logger

# 1. Configuration (Railway Variables se uthayega)
API_KEY = os.getenv('ANGEL_API_KEY')
AUTH_TOKEN = os.getenv('ANGEL_AUTH_TOKEN')
USER_ID = os.getenv('ANGEL_USER_ID')
PASSWORD = os.getenv('ANGEL_PASSWORD')
TOTP_SECRET = os.getenv('ANGEL_TOTP_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Bot Initialization
bot = telebot.TeleBot(TELEGRAM_TOKEN)
obj = SmartConnect(api_key=API_KEY)

def login_angel():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()
        data = obj.generateSession(USER_ID, PASSWORD, totp)
        if data['status']:
            return "Bhai, Hanuman-Bot Angel One mein login ho gaya! 🚩"
        else:
            return f"Login Fail: {data['message']}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Telegram Commands ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Jai Shree Ram! 🙏\n\n"
        "Main hoon Hanuman-Bot. Main aapka Trading aur Freelancing dono kaam sambhaal sakta hoon.\n\n"
        "Commands:\n"
        "/login - Angel One connect karne ke liye\n"
        "/status - Market aur Account check karne ke liye\n"
        "/freelance - Naye projects ki update ke liye"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['login'])
def handle_login(message):
    bot.reply_to(message, "Rukiye bhai, login check kar raha hoon...")
    response = login_angel()
    bot.reply_to(message, response)

@bot.message_handler(commands=['status'])
def handle_status(message):
    # Abhi ke liye simple status, kal isme live profit/loss add karenge
    bot.reply_to(message, "Bot Active hai! Kal subah 9:15 par market scanning shuru hogi.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # Ye part aapke AI Studio wale dimaag se baat karega
    bot.reply_to(message, "Bhai, aapka message mil gaya. Main is par kaam kar raha hoon...")

# Start the Bot
if __name__ == "__main__":
    logger.info("Hanuman-Bot is starting...")
    bot.infinity_polling()
