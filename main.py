import os
import time
import threading
import logging
from flask import Flask
import telebot
import google.generativeai as genai

# ==========================================
# ⚙️ 1. CONFIGURATION & SETUP
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
AUTHORIZED_USER_ID = 6119855904  # Sirf is ID ko reply milega

# Initialize Telegram Bot
try:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
except Exception as e:
    logging.error(f"❌ Telegram Token Error: {e}")
    bot = None

# Initialize Gemini AI Model
ai_model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 🛡️ THE FIX: SAFETY SETTINGS (Block None for Trading/NISM Queries)
        my_safety_settings =[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        # Setup Model with Persona
        ai_model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction="Aap ek financial aur technical expert AI hain. Aapko hamesha aasan (simple) Hindi mein jawab dena hai.",
            safety_settings=my_safety_settings  # Safety filters disabled here!
        )
        logging.info("✅ Gemini AI Model Configured (Safety Filters: OFF)")
    except Exception as e:
        logging.error(f"❌ Gemini Setup Failed: {e}")

# ==========================================
# 🌐 2. FLASK WEB SERVER (RAILWAY KEEP-ALIVE)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Hanuman AI Bot is LIVE!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ==========================================
# 🤖 3. TELEGRAM BOT LOGIC
# ==========================================
if bot:
    @bot.message_handler(func=lambda message: True)
    def handle_messages(message):
        # SECURITY CHECK: Ignore strangers
        if message.from_user.id != AUTHORIZED_USER_ID:
            return 

        # Validate AI Configuration
        if not ai_model or not GEMINI_API_KEY:
            bot.reply_to(message, "⚠️ Error: Gemini API key set nahi hai.")
            return

        bot.send_chat_action(message.chat.id, 'typing')

        # Get AI Response
        try:
            response = ai_model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except Exception as e:
            logging.error(f"⚠️ AI Error: {e}")
            bot.reply_to(message, "⚠️ Jawab generate karne mein problem hui. (API Limit ya Network Error).")

# ==========================================
# 🚀 4. STARTUP LOOP
# ==========================================
if __name__ == "__main__":
    # Start Flask Server in Background
    threading.Thread(target=run_flask, daemon=True).start()

    # Start Telegram Bot
    if bot:
        logging.info("📡 Starting Telegram Polling...")
        while True:
            try:
                bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
            except Exception as e:
                logging.error(f"🚨 Polling Error: {e}")
                time.sleep(10)
    else:
        logging.critical("❌ Bot start nahi ho paya. Token check karein.")
        while True:
            time.sleep(60) # Keep container alive for Flask        
