import time
import requests
import pandas as pd
from config import SCAN_INTERVAL, MIN_VOLUME
from signals import generate_signal
from telegram_bot import send_signal

BINANCE_URL = "https://api.binance.us/api/v3"

def get_usdt_pairs():
    try:
        r = requests.get(f"{BINANCE_URL}/exchangeInfo", timeout=10)
        data = r.json()
        pairs = [s["symbol"] for s in data["symbols"]
                 if s["quoteAsset"]=="USDT" and s["status"]=="TRADING"]
        return pairs
    except Exception as e:
        print("Error fetching pairs:", e)
        return []

def get_klines(symbol, interval="5m", limit=200, retries=3):
    for _ in range(retries):
        try:
            params = {"symbol": symbol, "interval": interval, "limit": limit}
            r = requests.get(f"{BINANCE_URL}/klines", params=params, timeout=10)
            data = r.json()
            if not isinstance(data, list) or len(data) < 2:
                continue
            df = pd.DataFrame(data, columns=[
                "time","open","high","low","close","volume",
                "close_time","quote_asset_volume","trades",
                "taker_base","taker_quote","ignore"
            ])
            df = df[["time","open","high","low","close","volume"]]
            df[["close","volume"]] = df[["close","volume"]].astype(float)
            return df
        except Exception as e:
            print(f"{symbol} klines error: {e}")
            time.sleep(1)
    return None

print("🚀 Railway Crypto Signal Bot Started")

pairs = get_usdt_pairs()
print("Total USDT pairs detected:", len(pairs))

while True:
    for symbol in pairs:
        try:
            df5 = get_klines(symbol, "5m")
            df1 = get_klines(symbol, "1h")

            if df5 is None or df1 is None:
                print(symbol, "skipped: insufficient data")
                continue

            if df5["volume"].iloc[-1] < MIN_VOLUME:
                print(symbol, "skipped: low volume", df5["volume"].iloc[-1])
                continue

            signal = generate_signal(df5, df1)
            print(symbol, "->", "Signal:", signal)

            if signal:
                send_signal(symbol, signal)

            time.sleep(0.25)  # avoid hitting rate limits

        except Exception as e:
            print(symbol, "error:", e)

    time.sleep(SCAN_INTERVAL)
