from indicators import rsi, ema, volume_spike


def detect_trend(df):

    ema50 = ema(df["close"], 50)
    ema200 = ema(df["close"], 200)

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return "up"

    return "down"


def generate_signal(df5, df1):

    trend = detect_trend(df1)

    df5 = rsi(df5)

    ema9 = ema(df5["close"], 9)
    ema21 = ema(df5["close"], 21)

    rsi_val = df5["rsi"].iloc[-1]

    vol = volume_spike(df5)

    price_now = df5["close"].iloc[-1]
    price_prev = df5["close"].iloc[-2]

    change = (price_now - price_prev) / price_prev * 100

    score = 0

    if trend == "up":
        score += 30

    if ema9.iloc[-1] > ema21.iloc[-1]:
        score += 25

    if vol:
        score += 20

    if 40 < rsi_val < 70:
        score += 15

    if change > 0.3:
        score += 10

    if score >= 60:

        return {
            "direction": "LONG",
            "entry": price_now,
            "score": score
        }

    score = 0

    if trend == "down":
        score += 30

    if ema9.iloc[-1] < ema21.iloc[-1]:
        score += 25

    if vol:
        score += 20

    if 30 < rsi_val < 60:
        score += 15

    if change < -0.3:
        score += 10

    if score >= 60:

        return {
            "direction": "SHORT",
            "entry": price_now,
            "score": score
        }

    return None
