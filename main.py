import os
import threading
import telebot
import pyotp
import google.generativeai as genai
from flask import Flask
from SmartApi import SmartConnect

# 1. Fetch Environment Variables EXACTLY as requested
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

ANGEL_API_KEY = os.environ.get('ANGEL_API_KEY')
ANGEL_CLIENT_ID = os.environ.get('ANGEL_CLIENT_ID')
ANGEL_PASSWORD = os.environ.get('ANGEL_PASSWORD')
ANGEL_TOTP_SECRET = os.environ.get('ANGEL_TOTP_SECRET')

# Check if vital keys are missing
if not TELEGRAM_BOT_TOKEN or not GEMINI_KEY:
    print("WARNING: TELEGRAM_BOT_TOKEN or GEMINI_KEY is missing.")

# 2. Configure Gemini API (Stable 1.5-flash, NO v1beta)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Global variable to hold SmartApi session
smart_api = None

# 4. Define Bot Message Handlers

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Jai Shri Ram! Welcome to Hanuman Bot. 🕉️\n\n"
        "I am powered by Gemini 1.5 Flash. You can ask me anything!\n\n"
        "To connect your Angel One Account, send the command:\n"
        "/login"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['login'])
def login_angel_one(message):
    global smart_api
    bot.reply_to(message, "Attempting to login to Angel One... Please wait.")
    
    try:
        if not all([ANGEL_API_KEY, ANGEL_CLIENT_ID, ANGEL_PASSWORD, ANGEL_TOTP_SECRET]):
            bot.reply_to(message, "❌ Angel One credentials are missing in Railway Environment Variables.")
            return

        # Initialize SmartConnect
        smart_api = SmartConnect(api_key=ANGEL_API_KEY)
        
        # Generate TOTP dynamically using the Secret key
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        
        # Login
        data = smart_api.generateSession(ANGEL_CLIENT_ID, ANGEL_PASSWORD, totp)
        
        if data['status']:
            bot.reply_to(message, f"✅ Angel One Login Successful! Welcome {ANGEL_CLIENT_ID}.")
        else:
            bot.reply_to(message, f"❌ Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred during login: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_normal_chat(message):
    # This handles normal text and passes it to Gemini AI
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        error_msg = "Sorry, my AI brain encountered an error. Please try again."
        print(f"Gemini API Error: {e}")
        bot.reply_to(message, error_msg)

# 5. Set up Flask Server for Railway Health Checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Hanuman Bot is alive and running smoothly!", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 6. Run Flask and Bot together using threading
if __name__ == '__main__':
    # Start the Flask web server in a background thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("Starting Hanuman Telegram Bot...")
    # Start the Telegram bot loop
    bot.infinity_polling(timeout=10, long_polling_timeout=5)     
