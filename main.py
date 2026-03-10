import time
import pandas as pd
from binance.client import Client

from config import TOP_COINS, SCAN_INTERVAL
from signals import generate_signal
from telegram_bot import send_signal


client = Client()


def get_klines(symbol, interval, limit=200):

    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)

    df = pd.DataFrame(klines, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df


print("🚀 AI Signal Bot Started")

while True:

    for symbol in TOP_COINS:

        try:

            df_5m = get_klines(symbol,"5m")
            df_1h = get_klines(symbol,"1h")

            signal = generate_signal(df_5m, df_1h)

            if signal:

                send_signal(symbol, signal)

                print(symbol, signal)

        except Exception as e:

            print(symbol, "error", e)

    time.sleep(SCAN_INTERVAL)
