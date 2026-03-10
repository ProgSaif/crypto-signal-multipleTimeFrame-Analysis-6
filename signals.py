# signals.py
import requests
import pandas as pd
import numpy as np

# ===== PARAMETERS =====
EMA_FAST = 9
EMA_SLOW = 21
RSI_PERIOD = 14
PRICE_MOVE_THRESHOLD = 0.001
VOLUME_MULTIPLIER = 0.2
RSI_LONG_MAX = 90
RSI_SHORT_MIN = 10
CONFIDENCE_THRESHOLD = 50
ATR_MULTIPLIER = 3
MIN_DAILY_VOLUME = 0
KLINE_LIMIT = 200

# ===== Helper Functions =====
def get_klines(symbol, interval="1h", limit=KLINE_LIMIT, retries=3):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if not isinstance(data, list):
                raise ValueError(f"Unexpected response: {data}")
            df = pd.DataFrame(data, columns=[
                "open_time","open","high","low","close",
                "volume","close_time","quote_asset_volume",
                "trades","taker_base","taker_quote","ignore"
            ])
            df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
            return df
        except Exception as e:
            print(f"{symbol} -> Kline fetch attempt {attempt+1} failed: {e}")
    return None

def calculate_rsi(df, period=RSI_PERIOD):
    if df is None or df.empty: return None
    delta = df["close"].diff()
    gain = np.where(delta>0, delta, 0)
    loss = np.where(delta<0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else None

def calculate_ema_trend(df, fast=EMA_FAST, slow=EMA_SLOW):
    if df is None or df.empty: return None
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "up"
    elif ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        return "down"
    else:
        return "flat"

def calculate_atr(df, period=14):
    if df is None or df.empty: return None
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    tr = pd.DataFrame({"hl": high_low, "hc": high_close, "lc": low_close}).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr.iloc[-1] if not atr.empty else None

def detect_volume_spike(df, multiplier=VOLUME_MULTIPLIER):
    if df is None or df.empty: return False
    avg_volume = df["volume"].rolling(20).mean()
    current_volume = df["volume"].iloc[-1]
    if avg_volume.empty or current_volume == 0: return False
    return current_volume > (avg_volume.iloc[-1] * multiplier)

def calculate_signal(symbol, df, last_price, change_pct, daily_volume):
    if df is None or df.empty or len(df) < EMA_SLOW:
        reason = "insufficient kline data"
        print(f"{symbol} skipped: {reason}")
        return None

    if daily_volume < MIN_DAILY_VOLUME:
        reason = f"low daily volume ({daily_volume})"
        print(f"{symbol} skipped: {reason}")
        return None

    rsi_val = calculate_rsi(df)
    ema_trend = calculate_ema_trend(df)
    atr_val = calculate_atr(df)
    vol_spike = detect_volume_spike(df)

    print(f"{symbol} -> RSI: {rsi_val}, Trend: {ema_trend}, VolumeSpike: {vol_spike}, Change: {change_pct:.4f}, Volume: {daily_volume}")

    trade_type = None
    if change_pct > PRICE_MOVE_THRESHOLD and ema_trend == "up" and (rsi_val is None or rsi_val < RSI_LONG_MAX) and vol_spike:
        trade_type = "LONG"
    elif change_pct < -PRICE_MOVE_THRESHOLD and ema_trend == "down" and (rsi_val is None or rsi_val > RSI_SHORT_MIN) and vol_spike:
        trade_type = "SHORT"

    if trade_type is None:
        print(f"{symbol} -> Signal: None (conditions not met)")
        return None

    if atr_val is None: atr_val = last_price * 0.01
    if trade_type == "LONG":
        entry = last_price
        sl = entry - atr_val * ATR_MULTIPLIER
        tp1 = entry + atr_val * ATR_MULTIPLIER
        tp2 = entry + atr_val * ATR_MULTIPLIER * 2
        tp3 = entry + atr_val * ATR_MULTIPLIER * 3
    else:
        entry = last_price
        sl = entry + atr_val * ATR_MULTIPLIER
        tp1 = entry - atr_val * ATR_MULTIPLIER
        tp2 = entry - atr_val * ATR_MULTIPLIER * 2
        tp3 = entry - atr_val * ATR_MULTIPLIER * 3

    score = int(abs(change_pct)*100) + (20 if vol_spike else 0) + (20 if ema_trend == ("up" if trade_type=="LONG" else "down") else 0)
    score = min(score, 100)
    if score < CONFIDENCE_THRESHOLD:
        print(f"{symbol} -> Signal rejected: low confidence ({score})")
        return None

    return {
        "coin": symbol.replace("USDT",""),
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "trade_type": trade_type,
        "confidence": score
    }
