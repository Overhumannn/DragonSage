import time  # Для работы с временными метками и задержками
import aiohttp  # Для выполнения асинхронных HTTP-запросов
import humanize  # Для удобного форматирования времени (например, "5 minutes ago")
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message  # Для обработки сообщений Telegram
from bot import dp  # Для доступа к диспетчеру вашего бота
from binance.client import Client  # Для взаимодействия с API Binance
from config import settings  # Для получения настроек, включая API ключи
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя
import logging  # Для логирования

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Binance клиента
binance_client = Client(settings.binance_api_key, settings.binance_api_secret)

# Уникальные эмодзи для сделок
strength_emojis = ["💪", "🧠", "🏋️", "🥇", "🏆", "⚔️", "🔧", "🏅", "🎯", "🚀"]

# Функция для получения данных о крупных сделках через API Binance
async def fetch_large_orders(symbol, minutes=60):
    url = f"https://api.binance.com/api/v3/aggTrades"
    params = {
        'symbol': symbol.upper().replace("/", ""),  # Преобразуем символ пары в нужный формат
        'limit': 1000,  # Лимит на количество сделок за один запрос
    }

    start_time = int(time.time() * 1000) - minutes * 60 * 1000

    all_trades = []
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    # Фильтрация сделок по времени
                    trades_in_timeframe = [trade for trade in data if int(trade['T']) >= start_time]
                    all_trades.extend(trades_in_timeframe)

                    # Если получено меньше 1000 сделок или уже собрали 10 000 сделок, завершаем сбор данных
                    if len(data) < 1000 or len(all_trades) >= 10000:
                        break

                    # Устанавливаем fromId для следующего запроса, чтобы продолжить с последней сделки
                    params['fromId'] = data[-1]['a']
                else:
                    raise Exception(f"Ошибка загрузки данных: {response.status} - {await response.text()}")

            # Если собрано 10 000 сделок, прерываем цикл
            if len(all_trades) >= 10000:
                break

    # Проверяем и корректируем обработку данных об объеме
    large_orders = sorted(all_trades, key=lambda x: float(x['q']), reverse=True)[:10]

    return large_orders

# Обработчик команды /whales
@dp.message(Command(commands=['whales']))
async def send_large_orders(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        language = get_user_language(message.from_user.id)  # Предполагается, что функция синхронная
        is_russian = (language == 'ru')

        # Разделение сообщения на символ
        args = message.text.split()[1:]
        if len(args) != 1:
            if is_russian:
                await message.reply("❗️ Пожалуйста, укажите торговую пару. Например: /киты BTCUSDT")
            else:
                await message.reply("❗️ Please specify the trading pair. For example: /whales BTCUSDT")
            return

        symbol = args[0]

        # Получаем данные о крупных сделках (за последние 60 минут по умолчанию)
        large_orders = await fetch_large_orders(symbol)

        if large_orders:
            if is_russian:
                orders_message = f"🐋 **{symbol.upper()}** на Binance\n🐋 **Крупнейшие ордера за последние 60 минут**\n\n"
            else:
                orders_message = f"🐋 **{symbol.upper()}** on Binance\n🐋 **Biggest Orders in the Last 60 Minutes**\n\n"

            for i, order in enumerate(large_orders):  # Выводим топ-10 крупнейших ордеров
                volume = float(order['q'])
                price = float(order['p'])
                volume_usdt = volume * price  # Переводим объем в USDT
                formatted_volume = f"{volume_usdt / 1000000:.2f}M USDT" if volume_usdt >= 1000000 else f"{volume_usdt:.2f} USDT"
                order_time = humanize.naturaltime(time.time() - (int(order['T']) / 1000))
                emoji = strength_emojis[i % len(strength_emojis)]  # Выбираем уникальный эмодзи
                if is_russian:
                    orders_message += f"{emoji} **{formatted_volume}** | {order_time}\n"
                else:
                    orders_message += f"{emoji} **{formatted_volume}** | {order_time}\n"

            # Отправляем сообщение пользователю
            await message.reply(orders_message, parse_mode="Markdown")
        else:
            if is_russian:
                await message.reply("❌ Не удалось найти крупные ордера за указанный промежуток времени.")
            else:
                await message.reply("❌ No large orders found for the specified time period.")

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        # В случае ошибки отправляем сообщение на нужном языке
        if 'is_russian' in locals() and is_russian:
            await message.reply("⚠️ Произошла ошибка при получении данных о сделках.")
        else:
            await message.reply("⚠️ An error occurred while fetching trade data.")
