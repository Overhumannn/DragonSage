import aiohttp  # Для выполнения асинхронных HTTP-запросов
import random  # Для генерации случайных эмодзи
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message  # Для обработки сообщений Telegram
from bot import dp  # Для доступа к диспетчеру вашего бота
from config import settings  # Для получения настроек, включая API ключи


# Функция для получения данных о криптовалютах через API CryptoCompare
async def fetch_best_cryptos():
    url = "https://min-api.cryptocompare.com/data/top/mktcapfull"
    params = {
        'limit': 100,  # Количество топ-криптовалют для анализа
        'tsym': 'USD',
        'api_key': settings.crypto_api_key  # Используем API-ключ из настроек
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                cryptos = data['Data']

                # Фильтруем криптовалюты с имеющимся ключом 'CHANGEPCT24HOUR' и конвертируем его в число
                valid_cryptos = [
                    crypto for crypto in cryptos
                    if 'DISPLAY' in crypto and 'USD' in crypto['DISPLAY'] and 'CHANGEPCT24HOUR' in crypto['DISPLAY']['USD']
                ]

                # Отбираем 5 криптовалют с наибольшим положительным изменением цены за 24 часа
                best_cryptos = sorted(
                    valid_cryptos,
                    key=lambda x: float(x['DISPLAY']['USD']['CHANGEPCT24HOUR']),
                    reverse=True
                )[:5]

                return best_cryptos
            else:
                raise Exception(f"Ошибка загрузки данных: {response.status}")

# Обработчик команды /best или /лучшие
@dp.message(Command(commands=['best']))
async def send_best_cryptos(message: Message):
    try:
        # Набор случайных эмодзи для разнообразия текста
        emojis = ["📈", "🚀", "💹", "📊", "💰", "🎉"]

        # Получаем данные о лучших криптовалютах
        best_cryptos = await fetch_best_cryptos()

        if best_cryptos:
            # Формируем сообщение
            best_message = f"Gainers in Top 100 (24h) {random.choice(emojis)}\n"
            for crypto in best_cryptos:
                coin_info = crypto['CoinInfo']
                display_info = crypto['DISPLAY']['USD']

                name = coin_info['FullName']
                symbol = coin_info['Name']
                price = display_info['PRICE']
                change = f"{display_info['CHANGEPCT24HOUR']}%"
                best_message += f"{name} - ${symbol} | {change} {random.choice(emojis)}\n{price}\n"

            # Отправляем сообщение пользователю
            await message.answer(best_message)
        else:
            await message.reply("Не удалось получить данные о криптовалютах.")

    except Exception as e:
        await message.reply("Произошла ошибка при получении данных о криптовалютах.")
        print(f"Ошибка: {e}")
