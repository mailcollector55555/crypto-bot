import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    print("Telegram status:", r.status_code)
    print("Telegram response:", r.text)

print("Bot test démarré")
print("TELEGRAM_TOKEN exists:", bool(TELEGRAM_TOKEN))
print("CHAT_ID exists:", bool(CHAT_ID))

send_telegram("✅ TEST Railway vers Telegram")
