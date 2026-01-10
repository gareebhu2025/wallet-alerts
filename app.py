import os
import time
import json
import asyncio
import requests
import websockets

# ================= CONFIG =================

NOW_API_KEY = os.getenv("e99c8e4f-eac6-4ffa-89c4-fd9a47032f81")
TG_BOT_TOKEN = os.getenv("8584445318:AAGByyX2tJQvDs7VKj_k-25kQ5l8NzShkNQ")
TG_CHAT_ID = os.getenv("1784786973")

WATCH = {
    "BTC": ["bc1q898qd7frueve5gw5lrsyyqd3juav67gwh020gd"],
    "LTC": ["LZWu9oo4veQKmMaY83JCeU2YUqDeffaMwG"],
    "ETH": ["0xB5414bB4380b2704C79c2F577821C58Ea735D56C".lower()],
    "BSC": ["0xB5414bB4380b2704C79c2F577821C58Ea735D56C".lower()],
    "TRON": ["TE9J3sMABj84mGhVibfyctkqQYKDS8gtk1"]
}

# ERC20 contracts
USDC_ETH = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48".lower()
USDT_BSC = "0x55d398326f99059ff775485246999027b3197955".lower()

# ================= TELEGRAM =================

def tg(msg):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TG_CHAT_ID,
        "text": msg
    })

# ================= BTC / LTC =================

def check_utxo(chain, addr):
    url = f"https://api.nownodes.io/v2/address/{addr}"
    r = requests.get(url, headers={"api-key": NOW_API_KEY}, timeout=10).json()

    for tx in r.get("txs", []):
        conf = tx.get("confirmations", 0)
        status = "PENDING" if conf == 0 else "CONFIRMED"

        msg = (
            f"{'🟡' if conf == 0 else '🟢'} Incoming ({status})\n\n"
            f"Coin: {chain}\n"
            f"Amount: {tx.get('value')} {chain}\n"
            f"Confirmations: {conf}\n"
            f"TxID: {tx.get('txid')}"
        )
        tg(msg)

# ================= ETH / ERC20 / BEP20 =================

async def evm_listener(wss_url, chain):
    async with websockets.connect(wss_url) as ws:
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"]
        }))

        while True:
            data = json.loads(await ws.recv())
            tx_hash = data.get("params", {}).get("result")
            if not tx_hash:
                continue

            tx = requests.post(
                wss_url.replace("wss://", "https://").replace("/wss/", "/"),
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionByHash",
                    "params": [tx_hash],
                    "id": 1
                }
            ).json().get("result")

            if not tx:
                continue

            to = (tx.get("to") or "").lower()
            value = int(tx.get("value", "0x0"), 16)

            if chain == "ETH" and to in WATCH["ETH"]:
                tg(
                    f"🟡 Incoming (PENDING)\n\n"
                    f"Coin: ETH\n"
                    f"Amount: {value / 1e18} ETH\n"
                    f"TxID: {tx_hash}"
                )

            if chain == "BSC" and to in WATCH["BSC"]:
                tg(
                    f"🟡 Incoming (PENDING)\n\n"
                    f"Coin: BNB / BEP20\n"
                    f"TxID: {tx_hash}"
                )

# ================= TRC20 (CONFIRMED ONLY) =================

def check_trc20(addr):
    url = f"https://api.trongrid.io/v1/accounts/{addr}/transactions/trc20"
    r = requests.get(url, timeout=10).json()

    for tx in r.get("data", []):
        if tx.get("token_info", {}).get("symbol") == "USDT":
            amount = int(tx["value"]) / 1e6
            tg(
                f"🟢 Incoming (CONFIRMED)\n\n"
                f"Coin: USDT (TRC20)\n"
                f"Amount: {amount} USDT\n"
                f"TxID: {tx['transaction_id']}"
            )

# ================= MAIN =================

async def main():
    asyncio.create_task(
        evm_listener(f"wss://eth.nownodes.io/wss/{NOW_API_KEY}", "ETH")
    )
    asyncio.create_task(
        evm_listener(f"wss://bsc.nownodes.io/wss/{NOW_API_KEY}", "BSC")
    )

    while True:
        for a in WATCH["BTC"]:
            check_utxo("BTC", a)
        for a in WATCH["LTC"]:
            check_utxo("LTC", a)
        for a in WATCH["TRON"]:
            check_trc20(a)

        time.sleep(30)

asyncio.run(main())
