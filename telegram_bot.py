import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_signal(symbol, signal):

    text = f"""
🚀 {symbol} SIGNAL

Direction: {signal['direction']}
Entry: {signal['entry']}

Confidence: {signal['score']}%

#CryptoSignal
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }

    requests.post(url, data=data)
