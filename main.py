import requests
import time
import os

wallets = [
    "TFdffZ2EGx4xTqJhzMGYNr1rvemUUKCv3R",
    "TB7THSyAgjX2rbFisTYi1ygot1TNCygRXY",
    "TMFWs9weTrzwJLTDQEToHbSWgHpyBF6CxQ",
    "TPjfN8WypFkwRcoCExib45RHjzQhwMDrQh"
]

TELEGRAM_TOKEN = os.getenv("8564707764:AAF71P-mG0_7QRqughHRINDCRlO0JcoRCqo")
CHAT_ID = os.getenv("8393689976")

def get_last_tx(address):
    url = f"https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=1&address={address}"
    r = requests.get(url)
    data = r.json()
    tx = data.get("data", [])
    return tx[0] if tx else None

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

last_seen = {}

print("🚀 Bot lancé...")

while True:
    for i, w in enumerate(wallets):
        tx = get_last_tx(w)
        if tx:
            tx_id = tx["hash"]
            amount = int(tx.get("amount", 0)) / 1_000_000

            if w not in last_seen:
                last_seen[w] = tx_id
            elif last_seen[w] != tx_id:
                last_seen[w] = tx_id

                msg = f"""
💰 NEW USDT RECEIVED

Wallet #{i+1}
{w}

Amount: {amount} USDT
TX: {tx_id}
"""
                send(msg.strip())

    time.sleep(30)
