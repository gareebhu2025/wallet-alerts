from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ===== TELEGRAM SENDER =====
def send_telegram(msg: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN or CHAT_ID missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload, timeout=10)

# ===== WEBHOOK ENDPOINT =====
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

    # 🛑 Anti-spam (ignore zero / dust tx)
    if amount <= 0 or usd <= 0:
        return jsonify({"ignored": True})

    msg = f"""
💰 <b>{symbol} Incoming ({status})</b>

🌐 <b>Network:</b> {chain}
📦 <b>Amount:</b> {amount} {symbol}
💵 <b>Value:</b> ${usd:.2f}

👛 <b>Wallet:</b>
<code>{address}</code>

🔗 <a href="{tx_url}">View Transaction</a>
"""

    send_telegram(msg.strip())
    return jsonify({"ok": True})

# ===== HEALTH CHECK =====
@app.route("/")
def home():
    return "Wallet Alert Server Running"

# ===== REQUIRED FOR RAILWAY =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
