import pandas as pd

def rsi(df, period=14):

    delta = df["close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss

    df["rsi"] = 100 - (100 / (1 + rs))

    return df


def ema(series, period):

    return series.ewm(span=period, adjust=False).mean()


def volume_spike(df):

    avg = df["volume"].rolling(20).mean()

    return df["volume"].iloc[-1] > avg.iloc[-1] * 1.5
