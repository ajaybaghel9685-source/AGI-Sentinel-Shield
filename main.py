import os
from SmartApi import SmartConnect
import google.generativeai as genai

# Railway variables connect honge
api_key = os.getenv("ANGEL_API_KEY")
user_id = os.getenv("ANGEL_USER_ID")
password = os.getenv("ANGEL_PASSWORD")
totp_token = os.getenv("ANGEL_TOTP_TOKEN")
gemini_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-pro')

def start_bot():
    try:
        obj = SmartConnect(api_key=api_key)
        session = obj.generateSession(user_id, password, totp_token)
        print("Bhai, Hanuman-Bot login ho gaya!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_bot()
