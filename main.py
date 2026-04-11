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

# Angel One requires Symbol Tokens for orders. Add your required tokens here.
SYMBOL_TOKENS = {
    "RELIANCE": "2885",
    "SBIN": "3045",
    "TCS": "11536",
    "INFY": "1594",
    "HDFCBANK": "1333",
    "TATASTEEL": "3499"
}

# 4. Define Bot Message Handlers

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Jai Shri Ram! Welcome to Hanuman Bot. 🕉️\n\n"
        "I am powered by Gemini 1.5 Flash. Ask me anything!\n\n"
        "📈 *Trading Commands:*\n"
        "/login - Connect to Angel One\n"
        "/buy [SYMBOL] [QTY] - Place Market Buy Order (e.g., /buy SBIN 1)\n"
        "/sell [SYMBOL] [QTY] - Place Market Sell Order (e.g., /sell SBIN 1)\n"
        "/status - Check Funds & Orders"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['login'])
def login_angel_one(message):
    global smart_api
    bot.reply_to(message, "Attempting to login to Angel One... Please wait.")
    
    try:
        if not all([ANGEL_API_KEY, ANGEL_CLIENT_ID, ANGEL_PASSWORD, ANGEL_TOTP_SECRET]):
            bot.reply_to(message, "❌ Angel One credentials are missing in Railway Environment Variables.")
            return

        smart_api = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        data = smart_api.generateSession(ANGEL_CLIENT_ID, ANGEL_PASSWORD, totp)
        
        if data['status']:
            bot.reply_to(message, f"✅ Angel One Login Successful! Welcome {ANGEL_CLIENT_ID}.")
        else:
            bot.reply_to(message, f"❌ Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred during login: {str(e)}")

def place_order(message, transaction_type):
    global smart_api
    if smart_api is None:
        bot.reply_to(message, "❌ Please /login first to use trading features.")
        return

    try:
        args = message.text.upper().split()
        if len(args) != 3:
            bot.reply_to(message, f"❌ Invalid format. Use: /{transaction_type.lower()} [SYMBOL] [QTY]\nExample: /{transaction_type.lower()} SBIN 1")
            return

        symbol = args[1]
        qty = args[2]

        if symbol not in SYMBOL_TOKENS:
            bot.reply_to(message, f"❌ Symbol '{symbol}' not found in internal dictionary. Please add its token in the code.")
            return

        token = SYMBOL_TOKENS[symbol]

        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": f"{symbol}-EQ",
            "symboltoken": token,
            "transactiontype": transaction_type,
            "exchange": "NSE",
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": qty
        }

        order_id = smart_api.placeOrder(orderparams)
        
        if order_id:
            bot.reply_to(message, f"✅ {transaction_type} Order Placed!\nSymbol: {symbol}\nQty: {qty}\nOrder ID: `{order_id}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Order failed. Please check Angel One app.")

    except Exception as e:
        bot.reply_to(message, f"❌ Order Error: {str(e)}")

@bot.message_handler(commands=['buy'])
def buy_command(message):
    place_order(message, "BUY")

@bot.message_handler(commands=['sell'])
def sell_command(message):
    place_order(message, "SELL")

@bot.message_handler(commands=['status'])
def status_command(message):
    global smart_api
    if smart_api is None:
        bot.reply_to(message, "❌ Please /login first.")
        return

    bot.reply_to(message, "Fetching account status...")
    try:
        # Fetch Funds
        rms_data = smart_api.rmsLimit()
        net_margin = "N/A"
        if rms_data and rms_data.get('status') and rms_data.get('data'):
            net_margin = rms_data['data'].get('net', 'N/A')

        # Fetch Active Orders
        order_book = smart_api.orderBook()
        active_orders = 0
        if order_book and order_book.get('status') and order_book.get('data'):
            for order in order_book['data']:
                if order.get('orderstatus') in ['open', 'pending']:
                    active_orders += 1

        msg = (
            "📊 *Account Status*\n"
            f"💰 Available Funds: ₹{net_margin}\n"
            f"📝 Active/Pending Orders: {active_orders}"
        )
        bot.reply_to(message, msg, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching status: {str(e)}")

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
    
