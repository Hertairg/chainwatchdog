import time
import requests
from web3 import Web3
from .config import INFURA_URL, ETHERSCAN_API_KEY
from .heuristics import is_suspicious_tx
from .utils import send_telegram_alert, shorten_address

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

def get_latest_txs(address):
    url = f"https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }
    r = requests.get(url, params=params)
    return r.json().get("result", [])

WATCHED_ADDRESSES = [
    # Подозрительные адреса (можно подключать ML)
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",  # Пример: Binance wallet
]

def start_monitoring():
    seen = set()

    while True:
        for addr in WATCHED_ADDRESSES:
            txs = get_latest_txs(addr)
            for tx in txs:
                tx_hash = tx['hash']
                if tx_hash in seen:
                    continue
                seen.add(tx_hash)

                suspicious, reason = is_suspicious_tx(tx)
                if suspicious:
                    msg = (
                        f"🚨 Обнаружена подозрительная транзакция\n"
                        f"Адрес: {shorten_address(addr)}\n"
                        f"Сумма: {int(tx['value']) / 1e18:.4f} {tx.get('tokenSymbol', 'ETH')}\n"
                        f"Причина: {reason}\n"
                        f"TX: https://etherscan.io/tx/{tx_hash}"
                    )
                    print(msg)
                    send_telegram_alert(msg)

        time.sleep(30)  # Пауза между проверками
