from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}

    symbol = data.get("currency", "N/A")
    chain = data.get("chain", "N/A")
    amount = float(data.get("amount", 0))
    usd = float(data.get("amount_usd", 0))
    address = data.get("address", "N/A")
    tx_url = data.get("tx_url", "")

    if amount <= 0:
        return jsonify({"ignored": True})

    msg = (
        "💰 <b>Incoming Transaction</b>\n\n"
        f"🪙 Coin: <b>{symbol}</b>\n"
        f"🌐 Network: <b>{chain}</b>\n"
        f"💵 Amount: <b>{amount} {symbol}</b>\n"
        f"💲 USD: <b>${usd:.2f}</b>\n\n"
        f"👛 Wallet:\n<code>{address}</code>\n\n"
        f"🔗 {tx_url}"
    )

    send_telegram(msg)
    return jsonify({"ok": True})

@app.route("/")
def home():
    return "Wallet Alerts Running"
