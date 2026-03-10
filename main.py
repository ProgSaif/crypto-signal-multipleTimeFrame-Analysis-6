import time
import requests
import pandas as pd

from config import SCAN_INTERVAL, MIN_VOLUME
from signals import generate_signal
from telegram_bot import send_signal


BINANCE_URL = "https://api.binance.com/api/v3"


def get_usdt_pairs():

    r = requests.get(f"{BINANCE_URL}/exchangeInfo")

    data = r.json()

    pairs = []

    for s in data["symbols"]:

        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING":
            pairs.append(s["symbol"])

    return pairs


def get_klines(symbol, interval="5m", limit=200):

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:

        r = requests.get(f"{BINANCE_URL}/klines", params=params, timeout=10)

        data = r.json()

        if not isinstance(data,list):
            return None

        df = pd.DataFrame(data)

        df = df.iloc[:,:6]

        df.columns=["time","open","high","low","close","volume"]

        df["close"]=df["close"].astype(float)
        df["volume"]=df["volume"].astype(float)

        return df

    except:

        return None


print("🚀 ULTRA SCANNER BOT STARTED")

pairs = get_usdt_pairs()

print("Total pairs detected:",len(pairs))


while True:

    for symbol in pairs:

        try:

            df5 = get_klines(symbol,"5m")
            df1 = get_klines(symbol,"1h")

            if df5 is None or df1 is None:
                continue

            if df5["volume"].iloc[-1] < MIN_VOLUME:
                continue

            signal = generate_signal(df5,df1)

            if signal:

                send_signal(symbol,signal)

                print(symbol,signal)

            time.sleep(0.25)

        except Exception as e:

            print(symbol,"error",e)

    time.sleep(SCAN_INTERVAL)
