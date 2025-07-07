import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("IVASMS_EMAIL")
PASSWORD = os.getenv("IVASMS_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)
session = requests.Session()

def login():
    resp = session.post(
        "https://www.ivasms.com/login",
        data={"email": EMAIL, "password": PASSWORD},
        headers={"User-Agent": "Mozilla/5.0"},
    )
    return resp.ok and "dashboard" in resp.text.lower()

def get_latest_sms():
    resp = session.get("https://ivasms.com/portal/live")
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.find_all("tr")[1:]
    messages = [r.find_all("td")[-1].get_text(strip=True)
                for r in rows if r.find_all("td")]
    return messages

def main():
    if not login():
        print("❌ Login failed.")
        return

    print("✅ Logged in.")
    seen = set()

    while True:
        try:
            for msg in get_latest_sms():
                if msg and msg not in seen:
                    bot.send_message(chat_id=CHAT_ID, text=f"🔐 OTP: {msg}")
                    seen.add(msg)
            time.sleep(10)
        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(30)

if __name__ == "__main__":
    main()
