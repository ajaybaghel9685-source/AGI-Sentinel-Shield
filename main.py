import telebot
import os

# Railway Variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Jai Shree Ram! Hanuman-Bot chalu ho gaya hai.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Bhai, naya code kaam kar raha hai!")

bot.infinity_polling()
