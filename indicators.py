import pandas as pd

def calculate_rsi(df, period=14):
    delta = df["close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    df["RSI"] = rsi
    return df


def calculate_ema(df, period):
    return df["close"].ewm(span=period, adjust=False).mean()


def volume_spike(df):

    avg = df["volume"].rolling(20).mean()

    if df["volume"].iloc[-1] > avg.iloc[-1] * 1.5:
        return True

    return False
