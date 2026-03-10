# main.py
import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv
from signals import calculate_signal, get_klines
import requests

# ===== Load environment variables =====
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("BOT_TOKEN or CHANNEL_ID not set in .env")

bot = Bot(token=BOT_TOKEN)
posted = set()

# ===== Safe send function with auto-delete =====
async def send_message_safe(message, delete_after=3600):
    for i in range(3):
        try:
            msg = await bot.send_message(chat_id=CHANNEL_ID, text=message)
            return
        except Exception as e:
            print("Telegram send error:", e)
            await asyncio.sleep(10)

# ===== Scanner loop =====
async def scan_and_post():
    print("🚀 ULTRA SCANNER BOT STARTED")
    while True:
        try:
            # 1️⃣ Get all USDT pairs
            exchange_info = requests.get("https://api.binance.com/api/v3/exchangeInfo").json()
            symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'].endswith("USDT")]

            print(f"Total pairs detected: {len(symbols)}")

            for symbol in symbols:
                # Get 1h candles
                df = get_klines(symbol, interval="1h", limit=200)
                if df is None: continue

                last_price = df["close"].iloc[-1]
                change_pct = (last_price - df["close"].iloc[-2])/df["close"].iloc[-2] if len(df) > 1 else 0
                daily_volume = df["volume"].sum()

                signal = calculate_signal(symbol, df, last_price, change_pct, daily_volume)
                if signal:
                    key = f"{signal['coin']}_{signal['trade_type']}"
                    if key not in posted:
                        message = f"""
💹 ${signal['coin']} – {signal['trade_type']}

Entry: {signal['entry']:.6f}
SL: {signal['sl']:.6f}
TP1: {signal['tp1']:.6f}
TP2: {signal['tp2']:.6f}
TP3: {signal['tp3']:.6f}

Confidence: {signal['confidence']}%
DYOR — Follow for updates
"""
                        await send_message_safe(message)
                        posted.add(key)
                        print(f"{symbol} -> Signal posted: {signal['trade_type']}")

        except Exception as e:
            print("Scanner loop error:", e)

        await asyncio.sleep(60)  # every minute

# ===== Run bot =====
asyncio.run(scan_and_post())
