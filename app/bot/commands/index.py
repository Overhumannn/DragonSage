import aiohttp  # Для выполнения асинхронных HTTP-запросов
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message  # Для обработки сообщений Telegram
from bot import dp  # Для доступа к диспетчеру вашего бота
from config import settings  # Для получения настроек, включая API ключи
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя
import logging  # Для логирования

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция для получения топ-10 криптовалют по рыночной капитализации
async def fetch_top_cryptos():
    url = "https://min-api.cryptocompare.com/data/top/mktcapfull"
    params = {
        'limit': 10,
        'tsym': 'USD',
        'api_key': settings.crypto_api_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('Data', [])  # Возвращаем раздел Data с информацией о криптовалютах
            else:
                raise Exception(f"Ошибка загрузки данных: {response.status}")


# Обработчик команды /index 
@dp.message(Command(commands=['index']))
async def send_market_index(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        language = get_user_language(message.from_user.id)  # Предполагается, что функция синхронная
        is_russian = (language == 'ru')

        # Получаем данные о топ-10 криптовалютах
        cryptos = await fetch_top_cryptos()

        if not cryptos:
            if is_russian:
                await message.reply("❌ Не удалось получить данные о топ-10 криптовалютах.")
            else:
                await message.reply("❌ Failed to retrieve data for the top 10 cryptocurrencies.")
            return

        # Формируем сообщение
        if is_russian:
            text = "📈 **Топ-10 криптовалют по рыночной капитализации**:\n"
        else:
            text = "📈 **Top 10 Cryptocurrencies by Market Cap**:\n"

        for i, crypto in enumerate(cryptos, start=1):
            coin_info = crypto.get('CoinInfo', {})
            display_info = crypto.get('DISPLAY', {}).get('USD', {})

            name = coin_info.get('FullName', 'N/A')
            symbol = coin_info.get('Name', 'N/A')
            price = display_info.get('PRICE', 'N/A')
            change = display_info.get('CHANGEPCT24HOUR', 'N/A')

            if is_russian:
                price_text = f"💰 **Цена**: {price}"
                change_text = f"📉 **Изменение за 24ч**: {change}"
            else:
                price_text = f"💰 **Price**: {price}"
                change_text = f"📉 **24h Change**: {change}%"

            text += f"{i}. **{symbol} - {name}**\n   {price_text}\n   {change_text}\n"

        # Отправляем сообщение пользователю
        await message.answer(text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        # В случае ошибки отправляем сообщение на нужном языке
        if 'is_russian' in locals() and is_russian:
            await message.reply("⚠️ Произошла ошибка при получении рыночных данных.")
        else:
            await message.reply("⚠️ An error occurred while fetching market data.")
