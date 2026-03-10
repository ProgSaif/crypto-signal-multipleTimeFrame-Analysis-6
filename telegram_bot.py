import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_signal(symbol, signal):

    text = f"""
🚀 {symbol} SIGNAL

Direction: {signal['direction']}
Entry: {round(signal['entry'],4)}

Confidence: {signal['score']}%
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    })
