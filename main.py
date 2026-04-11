import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask

# ==========================================
# 1. Environment Variables & Constants
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ALLOWED_USER_ID = 6119855904

# ==========================================
# 2. Gemini API Configuration
# ==========================================
genai.configure(api_key=GEMINI_API_KEY)

# Safety filters ko BLOCK_NONE set karna taaki trading/NISM wale sawal block na hon
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

# Persona/System Instruction setup
system_instruction = (
    "Tumhara naam 'Hanuman AI' hai. Tum hamesha polite rahoge aur user ke "
    "sawalon ka jawab bilkul saral (simple) Hindi mein doge."
)

# Model initialize karna (gemini-1.5-flash fast aur accha hai)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    system_instruction=system_instruction
)

# ==========================================
# 3. Telegram Bot Setup
# ==========================================
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Security: Sirf specific User ID ko allow karein
    if message.from_user.id != ALLOWED_USER_ID:
        return # Baaki sabhi users ko completely ignore karega

    try:
        # Chat history/message Gemini ko bhejna
        response = model.generate_content(message.text)
        
        # Bot ka reply
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Maaf karna, ek error aayi hai: {str(e)}")

# ==========================================
# 4. Flask Server (For Railway / Keeping Alive)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Hanuman AI Telegram Bot is Running!"

def run_flask_server():
    # Port 8080 par Flask chalayen
    app.run(host="0.0.0.0", port=8080)

# ==========================================
# 5. Main Execution Thread
# ==========================================
if __name__ == "__main__":
    # Check karein ki Environment Variables set hain ya nahi
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        print("Error: TELEGRAM_BOT_TOKEN ya GEMINI_API_KEY environment variable missing hai!")
    else:
        # Flask server ko background thread mein start karein
        server_thread = threading.Thread(target=run_flask_server)
        server_thread.daemon = True
        server_thread.start()

        print("Hanuman AI Bot start ho raha hai...")
        
        # Telegram Bot ko continuously run karein
        bot.infinity_polling()    
