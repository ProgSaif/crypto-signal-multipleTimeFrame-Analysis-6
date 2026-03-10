import time
import requests
import pandas as pd

from config import TOP_COINS, SCAN_INTERVAL
from signals import generate_signal
from telegram_bot import send_signal


BINANCE_URL = "https://api.binance.com/api/v3/klines"


def get_klines(symbol, interval="5m", limit=200):

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:

        r = requests.get(BINANCE_URL, params=params, timeout=10)

        data = r.json()

        if not isinstance(data, list):
            print(symbol, "API error:", data)
            return None

        if len(data) == 0:
            return None

        df = pd.DataFrame(data)

        df = df.iloc[:, :6]

        df.columns = ["time","open","high","low","close","volume"]

        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        return df

    except Exception as e:

        print(symbol, "request error:", e)

        return None


print("🚀 Railway Crypto Signal Bot Started")


while True:

    for symbol in TOP_COINS:

        try:

            df5 = get_klines(symbol, "5m")
            df1 = get_klines(symbol, "1h")

            if df5 is None or df1 is None:
                continue

            if df5["volume"].iloc[-1] < 1000:
                continue

            signal = generate_signal(df5, df1)

            if signal:

                send_signal(symbol, signal)

                print(symbol, signal)

            time.sleep(0.4)

        except Exception as e:

            print(symbol, "error:", e)

    time.sleep(SCAN_INTERVAL)
