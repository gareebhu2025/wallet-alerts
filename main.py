from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}

    txid = data.get("txid", "N/A")
    chain = data.get("chain", "Unknown")
    symbol = data.get("currency", "N/A")
    amount = float(data.get("amount", 0))
    usd = float(data.get("amount_usd", 0))
    address = data.get("address", "N/A")
    status = data.get("status", "pending").upper()
    tx_url = data.get("tx_url", "")

    # 🚫 Prevent spam (ignore zero amount)
    if amount <= 0:
        return jsonify({"ignored": True})

    msg = f"""
💰 <b>{symbol} Incoming ({status})</b>

🔗 Network: <b>{chain}</b>
💵 Amount: <b>{amount} {symbol}</b>
💲 Value: <b>${usd:.2f}</b>

📍 Wallet:
<code>{address}</code>

🔎 <a href="{tx_url}">View Transaction</a>
"""

    send_telegram(msg)
    return jsonify({"ok": True})

@app.route("/")
def home():
    return "Wallet Alert Server Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
