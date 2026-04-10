import os
import threading
import logging
from flask import Flask
import telebot
import google.generativeai as genai

# ==========================================
# ⚙️ 1. CONFIGURATION & ENVIRONMENT VARIABLES
# ==========================================
# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
AUTHORIZED_USER_ID = 6119855904  # Sirf aapki ID allowed hai

# Initialize Telegram Bot
try:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
except Exception as e:
    logging.error(f"❌ Failed to initialize Telegram Bot. Check TELEGRAM_BOT_TOKEN: {e}")
    bot = None

# Initialize Gemini AI Model
ai_model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Using system_instruction to set the AI Persona (Helpful Expert in Simple Hindi)
        ai_model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction="Aap ek helpful expert AI assistant hain. Aapka kaam user ki madad karna hai. Aapko hamesha aasan (simple) Hindi bhasha mein hi jawab dena hai. Aap bahut polite aur smart hain."
        )
        logging.info("✅ Gemini AI Model Configured Successfully!")
    except Exception as e:
        logging.error(f"❌ Gemini configuration failed: {e}")
else:
    logging.warning("⚠️ GEMINI_API_KEY is missing from environment variables.")

# ==========================================
# 🌐 2. FLASK WEB SERVER (RAILWAY KEEP-ALIVE)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Hanuman AI Telegram Bot is ONLINE and running smoothly."

def run_flask_server():
    """Runs the Flask server in a background thread to satisfy Railway's health checks."""
    # Railway automatically provides a PORT environment variable. Defaults to 8080.
    port = int(os.environ.get("PORT", 8080))
    logging.info(f"🌐 Starting Flask Keep-Alive Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ==========================================
# 🤖 3. TELEGRAM BOT LOGIC & SECURITY
# ==========================================
if bot:
    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        # SECURITY CHECK: Ignore all users except the Authorized ID
        if message.from_user.id != AUTHORIZED_USER_ID:
            logging.warning(f"🔒 Unauthorized access attempt by User ID: {message.from_user.id}")
            return # Ignore silently without replying to strangers

        # Check if AI model is loaded and Key exists
        if not ai_model or not GEMINI_API_KEY:
            error_msg = "⚠️ <b>Error:</b> Meri AI API key (Gemini) set nahi hai ya invalid hai. Kripya apne server ke Environment Variables check karein."
            bot.reply_to(message, error_msg, parse_mode='HTML')
            return

        # Let the user know the bot is "Typing..."
        bot.send_chat_action(message.chat.id, 'typing')

        # Generate AI Response
        try:
            response = ai_model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except Exception as e:
            logging.error(f"⚠️ AI Generation Error: {e}")
            fallback_msg = "⚠️ Maaf kijiye, mujhe jawab sochne mein koi takleef ho rahi hai. Kripya check karein ki Gemini API key valid hai ya rate limit toh cross nahi ho gayi."
            bot.reply_to(message, fallback_msg)

# ==========================================
# 🚀 4. KICKSTART & IMMORTALITY LOOP
# ==========================================
if __name__ == "__main__":
    # A) Start Flask in a separate daemon thread
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()

    # B) Start Telegram Bot Polling
    if bot:
        logging.info("📡 Starting Telegram Polling (skip_pending=True)...")
        while True:
            try:
                # skip_pending=True ensures the bot doesn't spam you with old messages if it was offline
                bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
            except Exception as e:
                logging.error(f"🚨 Polling Exception: {e}")
                logging.info("🔄 Rebooting polling sequence in 10 seconds...")
            import time
            time.sleep(10)
    else:
        logging.critical("❌ Bot could not start. Please verify your TELEGRAM_BOT_TOKEN.")
        # Keep Flask running even if bot fails, so Railway container doesn't crash completely
        flask_thread.join()
