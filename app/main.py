
import sys
import os

# Добавляем корень проекта в sys.path, если его там нет
project_root = os.path.dirname(os.path.abspath(__file__)).rsplit('app', 1)[0]
if project_root not in sys.path:
    sys.path.append(project_root)

from app.bot.commands import gas
from bot import dp, bot  # Импорт диспетчера и экземпляра бота из модуля bot
import asyncio
import logging
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

# Start bot
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


