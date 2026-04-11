import os
import sys
import threading
import logging
import telebot
import google.generativeai as genai
from flask import Flask

# ==========================================
# 1. Environment Variables & SAFETY CHECK
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
# Railway par aapne jo bhi naam rakha ho (GEMINI_KEY ya GEMINI_API_KEY), ye dono catch kar lega
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY")

# NoneType Error Fix: Agar token None hai toh bot crash hone se pehle ruk jayega aur log dega
if not TELEGRAM_TOKEN or not GEMINI_KEY:
    print("=====================================================")
    print("CRITICAL ERROR: TELEGRAM_TOKEN ya GEMINI_KEY missing hai!")
    print("Kripya Railway ke 'Variables' tab me jaakar check karein.")
    print("=====================================================")
    sys.exit(1) # Execution yahin rok dega taaki 'telebot' crash na ho

ALLOWED_USER_ID = 6119855904

# ==========================================
# 2. Gemini API - Stable Implementation
# ==========================================
genai.configure(api_key=GEMINI_KEY)

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

system_instruction = (
    "Tumhara naam 'Hanuman' hai. Tum hamesha polite rahoge aur user ke "
    "sawalon ka jawab bilkul saral (simple) Hindi mein doge."
)

# 404 Error Fix: Using the stable model name directly
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
    # Sirf allowed user ID ko reply karega
    if message.from_user.id != ALLOWED_USER_ID:
        return

    try:
        # Generate answer from Gemini
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Maaf karna, ek error aayi hai: {str(e)}")

# ==========================================
# 4. Flask Server (Railway Compatibility)
# ==========================================
app = Flask(__name__)

# Flask ka development warning hide karne ke liye
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return "Hanuman Telegram Bot is Online and Running on Railway!"

def run_flask():
    # Railway randomly port assign karta hai, varna default 8080 lega
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==========================================
# 5. Main Execution Thread
# ==========================================
if __name__ == "__main__":
    print("Starting Flask Server...")
    # Flask ko background thread me chalayein
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Starting Hanuman Bot Infinity Polling...")
    # Telegram bot ko main thread me lagatar chalayein (stability ke liye)
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot Polling Error: {e}")
