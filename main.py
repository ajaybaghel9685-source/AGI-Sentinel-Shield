import os
import threading
import logging
import telebot
import google.generativeai as genai
from flask import Flask

# ==========================================
# 1. Environment Variables setup
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

# Aapki previous security requirement (Change it if you want)
ALLOWED_USER_ID = 6119855904 

# ==========================================
# 2. Gemini API - Latest Implementation
# ==========================================
genai.configure(api_key=GEMINI_KEY)

# Safety settings (BLOCK_NONE for all categories)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

# System Instruction
system_instruction = (
    "Tumhara naam 'Hanuman' hai. Tum hamesha polite rahoge aur user ke "
    "sawalon ka jawab bilkul saral (simple) Hindi mein doge."
)

# Initialize the stable 1.5 Flash model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    system_instruction=system_instruction
)

# ==========================================
# 3. Telegram Bot Setup
# ==========================================
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Security: Sirf allowed user ko reply karega
    if message.from_user.id != ALLOWED_USER_ID:
        return

    try:
        # Gemini se content generate karna
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Error aayi hai: {str(e)}")

# ==========================================
# 4. Flask Server (Railway Keep-Alive)
# ==========================================
app = Flask(__name__)

# Flask ka "Development Server" warning hide karne ke liye
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return "Hanuman Telegram Bot is Online and Active!"

def run_flask():
    # Railway automatically ek PORT environment variable assign karta hai
    # Agar na mile to default 8080 use karega
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==========================================
# 5. Main Execution
# ==========================================
if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not GEMINI_KEY:
        print("CRITICAL ERROR: TELEGRAM_TOKEN ya GEMINI_KEY environment variables set nahi hain!")
    else:
        print("Starting Flask Server & Hanuman Bot...")
        
        # Flask ko background thread mein start karein
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

        # Telegram bot ko main thread mein start karein
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
