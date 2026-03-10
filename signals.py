import pandas as pd
from indicators import calculate_rsi, calculate_ema, volume_spike


def detect_trend(df):

    ema50 = calculate_ema(df, 50)
    ema200 = calculate_ema(df, 200)

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return "up"

    return "down"


def generate_signal(df_5m, df_1h):

    trend = detect_trend(df_1h)

    df_5m = calculate_rsi(df_5m)

    ema9 = calculate_ema(df_5m, 9)
    ema21 = calculate_ema(df_5m, 21)

    rsi = df_5m["RSI"].iloc[-1]

    vol_spike = volume_spike(df_5m)

    price_now = df_5m["close"].iloc[-1]
    price_prev = df_5m["close"].iloc[-2]

    change = (price_now - price_prev) / price_prev * 100

    score = 0

    if trend == "up":
        score += 30

    if ema9.iloc[-1] > ema21.iloc[-1]:
        score += 25

    if vol_spike:
        score += 20

    if 40 < rsi < 70:
        score += 15

    if change > 0.3:
        score += 10

    if score >= 60:

        return {
            "direction": "LONG",
            "entry": round(price_now,4),
            "score": score
        }

    if trend == "down":
        score += 30

    if ema9.iloc[-1] < ema21.iloc[-1]:
        score += 25

    if vol_spike:
        score += 20

    if 30 < rsi < 60:
        score += 15

    if change < -0.3:
        score += 10

    if score >= 60:

        return {
            "direction": "SHORT",
            "entry": round(price_now,4),
            "score": score
        }

    return None
