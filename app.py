from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=10
    )

@app.route("/", methods=["GET"])
def home():
    return "Wallet Alert Server Running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}

    amount = float(data.get("amount", 0))
    if amount <= 0:
        return jsonify({"ignored": True})

    symbol = data.get("currency", "UNKNOWN")
    chain = data.get("chain", "UNKNOWN")
    usd = float(data.get("amount_usd", 0))
    address = data.get("address", "N/A")
    txid = data.get("txid", "N/A")
    status = data.get("status", "pending").upper()
    tx_url = data.get("tx_url", "")

    msg = f"""
💰 <b>{symbol} Incoming ({status})</b>

🔗 <b>Network:</b> {chain}
💵 <b>Amount:</b> {amount} {symbol}
💲 <b>Value:</b> ${usd:.2f}

📍 <b>Wallet:</b>
<code>{address}</code>

🔍 <a href="{tx_url}">View Transaction</a>
"""

    send_telegram(msg)
    return jsonify({"ok": True}), 200

# IMPORTANT: Railway needs this
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
