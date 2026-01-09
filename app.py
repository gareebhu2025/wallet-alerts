from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram env vars missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })

@app.route("/", methods=["GET"])
def home():
    return "Wallet Alert Server Running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}

    symbol = data.get("currency", "N/A")
    chain = data.get("chain", "N/A")
    amount = float(data.get("amount", 0))
    usd = float(data.get("amount_usd", 0))
    address = data.get("address", "N/A")
    tx_url = data.get("tx_url", "")
    status = data.get("status", "PENDING").upper()

    if amount <= 0:
        return jsonify({"ignored": True})

    msg = f"""
<b>💰 Incoming ({status})</b>

<b>Network:</b> {chain}
<b>Amount:</b> {amount} {symbol}
<b>Value:</b> ${usd:.2f}

<b>Wallet:</b>
<code>{address}</code>
