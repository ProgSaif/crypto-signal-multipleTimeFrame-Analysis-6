import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_signal(symbol, signal):
    try:
        text = f"""
🚀 {symbol} SIGNAL

Direction: {signal['direction']}
Entry: {round(signal['entry'], 8)}

Confidence: {signal['score']}%
"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
        if r.status_code != 200:
            print(f"Telegram error {r.status_code}: {r.text}")
        else:
            print(f"Telegram sent {symbol} signal successfully.")
    except Exception as e:
        print(f"Telegram exception for {symbol}: {e}")
