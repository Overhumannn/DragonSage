import sys
import os
import asyncio
import logging
from flask import Flask
import threading

# Добавляем корень проекта в sys.path, если его там нет
project_root = os.path.dirname(os.path.abspath(__file__)).rsplit('app', 1)[0]
if project_root not in sys.path:
    sys.path.append(project_root)

from app.bot.commands import gas
from bot import dp, bot  # Импорт диспетчера и экземпляра бота из модуля bot
from bot.commands import (
    start, 
    best, 
    charts, 
    compare, 
    convert, 
    description,
    gas, 
    google, 
    heatmap, 
    index,
    language, 
    market_summary, 
    price, 
    sentiment, 
    ta, 
    whales, 
    worst, 
    TOPS, 
    NFT, 
    NFT_PRO, 
    scam, 
    events, 
    ALLTIME, 
    dex, 
    aicommands,
    pro,
    help,
)

from locales import languages  # Импорт локалей
from bot.handlers import callbacks  # Импортируем обработчики callback-запросов

logging.basicConfig(level=logging.INFO)

# Flask app
app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is running!"


def run_flask():
    app.run(host="0.0.0.0", port=8080)


# Telegram bot
async def run_bot():
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Запускаем бота в основном потоке
    asyncio.run(run_bot())

