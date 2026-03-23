import requests
import time
import os

# ===== CONFIG WALLETS =====
wallets = [
    {
        "position": 1,
        "name": "SCI MARINODEUX",
        "address": "TFdffZ2EGx4xTqJhzMGYNr1rvemUUKCv3R"
    },
    {
        "position": 2,
        "name": "COURTAGE ENERGIE",
        "address": "TB7THSyAgjX2rbFisTYi1ygot1TNCygRXY"
    },
    {
        "position": 3,
        "name": "KBK",
        "address": "TMFWs9weTrzwJLTDQEToHbSWgHpyBF6CxQ"
    },
    {
        "position": 4,
        "name": "JFK PROD",
        "address": "TPjfN8WypFkwRcoCExib45RHjzQhwMDrQh"
    }
]

# ===== VARIABLES RAILWAY =====
TELEGRAM_TOKEN = "8564707764:AAF71P-mG0_7QRqughHRINDCRlO0JcoRCqo"
CHAT_ID = "-5147137068"

USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


def send_telegram(msg: str) -> None:
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram non configuré : TELEGRAM_TOKEN ou CHAT_ID manquant")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=15
        )
        print("Telegram status:", r.status_code)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Erreur envoi Telegram:", e)


def get_usdt_balance(address: str) -> float:
    url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()

    for token in data.get("trc20token_balances", []):
        if token.get("tokenId") == USDT_CONTRACT or token.get("tokenAbbr") == "USDT":
            return int(token.get("balance", 0)) / 1_000_000

    return 0.0


def get_latest_usdt_incoming(address: str):
    url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&limit=20&start=0&sort=-timestamp"

    try:
        r = requests.get(url, timeout=20)
        data = r.json()
        txs = data.get("data", [])

        for tx in txs:
            if tx.get("tokenName") == "Tether USD" and tx.get("toAddress") == address:
                return {
                    "hash": tx.get("hash"),
                    "amount": int(tx.get("amount", 0)) / 1_000_000,
                    "from": tx.get("ownerAddress")
                }

    except Exception as e:
        print(f"Erreur API sur {address}:", e)

    return None


def short_addr(addr: str) -> str:
    if not addr or len(addr) < 12:
        return str(addr)
    return f"{addr[:6]}...{addr[-6:]}"


def send_startup_report():
    lines = [
        "🚀 Bot démarré",
        "",
        "📊 Position actuelle des wallets :"
    ]

    for wallet in wallets:
        try:
            balance = get_usdt_balance(wallet["address"])
            lines.append(
                f'#{wallet["position"]} - {wallet["name"]}\n'
                f'Adresse: {wallet["address"]}\n'
                f'Solde: {balance:.2f} USDT\n'
            )
        except Exception as e:
            lines.append(
                f'#{wallet["position"]} - {wallet["name"]}\n'
                f'Adresse: {wallet["address"]}\n'
                f'Erreur lecture: {e}\n'
            )

    send_telegram("\n".join(lines))


def main():
    last_seen = {}

    print("🚀 Bot lancé et monitoring actif...")
    send_telegram("✅ Test Telegram OK - bot démarré avec succès")

    # Initialisation des dernières transactions connues
    for wallet in wallets:
        try:
            tx = get_latest_usdt_incoming(wallet["address"])
            last_seen[wallet["address"]] = tx["hash"] if tx else None
        except Exception as e:
            print(f"Erreur init sur {wallet['name']}:", e)
            last_seen[wallet["address"]] = None

    # Rapport de démarrage avec positions + soldes
    send_startup_report()

    while True:
        print("Check wallets...")

        for wallet in wallets:
            address = wallet["address"]

            try:
                tx = get_latest_usdt_incoming(address)
                if not tx:
                    continue

                tx_hash = tx["hash"]
                previous_hash = last_seen.get(address)

                if previous_hash is None:
                    last_seen[address] = tx_hash
                    continue

                if tx_hash != previous_hash:
                    last_seen[address] = tx_hash
                    current_balance = get_usdt_balance(address)

                    msg = (
                        f"💰 Nouveau crédit détecté\n\n"
                        f"Position: #{wallet['position']}\n"
                        f"Nom: {wallet['name']}\n"
                        f"Adresse: {address}\n\n"
                        f"Montant crédité: {tx['amount']:.2f} USDT\n"
                        f"Expéditeur: {short_addr(tx['from'])}\n"
                        f"Solde actuel: {current_balance:.2f} USDT\n"
                        f"TX: {tx_hash}"
                    )

                    send_telegram(msg)
                    print(f"✅ Crédit détecté sur #{wallet['position']} - {wallet['name']}")

            except Exception as e:
                print(f"Erreur sur {wallet['name']} ({address}): {e}")

        time.sleep(30)


if __name__ == "__main__":
    main()
