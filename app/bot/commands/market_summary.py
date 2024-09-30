import aiohttp  # Для выполнения асинхронных HTTP-запросов
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message  # Для обработки сообщений Telegram
from bot import dp  # Для доступа к диспетчеру вашего бота
from config import settings  # Для получения настроек, включая API ключи
from binance.client import Client  # Для взаимодействия с API Binance
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя
import asyncio  # Для асинхронных операций
import logging  # Для логирования

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

binance_client = Client(settings.binance_api_key, settings.binance_api_secret)

# Функция для получения данных Binance в отдельном потоке
def get_binance_tickers():
    return binance_client.get_ticker()

# Обработчик команды /market_summary
@dp.message(Command(commands=['market_summary']))
async def market_summary(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        language = get_user_language(message.from_user.id)  # Предполагается, что функция синхронная
        is_russian = (language == 'ru')

        # Асинхронно получаем данные от Binance в отдельном потоке
        tickers = await asyncio.to_thread(get_binance_tickers)

        if not tickers:
            if is_russian:
                await message.reply("❗️ Данные рынка недоступны.")
            else:
                await message.reply("❗️ No market data available.")
            return

        # Подсчет количества растущих и падающих криптовалют
        growing = sum(1 for ticker in tickers if float(ticker.get('priceChangePercent', 0)) > 0)
        falling = sum(1 for ticker in tickers if float(ticker.get('priceChangePercent', 0)) < 0)

        # Подсчет общего объема торгов и общего изменения цены
        total_volume = sum(float(ticker.get('quoteVolume', 0)) for ticker in tickers)
        average_change = (sum(float(ticker.get('priceChangePercent', 0)) for ticker in tickers) / len(tickers)) if tickers else 0

        # Находим топ-5 самых торгуемых пар
        top_pairs = sorted(tickers, key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)[:5]

        # Находим топ-3 растущих и топ-3 падающих криптовалют
        top_gainers = sorted(tickers, key=lambda x: float(x.get('priceChangePercent', 0)), reverse=True)[:3]
        top_losers = sorted(tickers, key=lambda x: float(x.get('priceChangePercent', 0)))[:3]

        # Формирование итогового сообщения
        if is_russian:
            summary_message = (
                f"📊 **Сводка рынка согласно данным Binance**:\n"
                f"🔼 **Растущие**: {growing}\n"
                f"🔽 **Падающие**: {falling}\n"
                f"💵 **Общий объем торгов (24ч)**: ${total_volume:,.2f} USD\n"
                f"📈 **Среднее изменение рынка**: {average_change:.2f}%\n\n"
                f"🏆 **Топ-5 торгуемых пар по объему**:\n"
            )
        else:
            summary_message = (
                f"📊 **Market Summary According to Binance Data**:\n"
                f"🔼 **Growing**: {growing}\n"
                f"🔽 **Falling**: {falling}\n"
                f"💵 **Total 24h Volume**: ${total_volume:,.2f} USD\n"
                f"📈 **Average Market Change**: {average_change:.2f}%\n\n"
                f"🏆 **Top 5 Trading Pairs by Volume**:\n"
            )

        for pair in top_pairs:
            symbol = pair.get('symbol', 'N/A')
            volume = float(pair.get('quoteVolume', 0))
            if is_russian:
                summary_message += f"   - **{symbol}**: ${volume:,.2f} USD\n"
            else:
                summary_message += f"   - **{symbol}**: ${volume:,.2f} USD\n"

        if is_russian:
            summary_message += "\n🚀 **Топ-3 растущих криптовалют**:\n"
        else:
            summary_message += "\n🚀 **Top 3 Gainers**:\n"

        for gain in top_gainers:
            symbol = gain.get('symbol', 'N/A')
            change = float(gain.get('priceChangePercent', 0))
            if is_russian:
                summary_message += f"   - **{symbol}**: {change:.2f}%\n"
            else:
                summary_message += f"   - **{symbol}**: {change:.2f}%\n"

        if is_russian:
            summary_message += "\n📉 **Топ-3 падающих криптовалют**:\n"
        else:
            summary_message += "\n📉 **Top 3 Losers**:\n"

        for loss in top_losers:
            symbol = loss.get('symbol', 'N/A')
            change = float(loss.get('priceChangePercent', 0))
            if is_russian:
                summary_message += f"   - **{symbol}**: {change:.2f}%\n"
            else:
                summary_message += f"   - **{symbol}**: {change:.2f}%\n"

        # Отправляем сообщение пользователю
        await message.reply(summary_message, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        # В случае ошибки отправляем сообщение на нужном языке
        if 'is_russian' in locals() and is_russian:
            await message.reply("⚠️ Произошла ошибка при получении рыночных данных.")
        else:
            await message.reply("⚠️ Failed to retrieve market summary.")
