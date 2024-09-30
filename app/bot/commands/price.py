import aiohttp
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from bot import dp  # Доступ к диспетчеру бота
from config import settings  # Для доступа к API ключам
from app.database.crud import get_user_language  # Функция для получения языка пользователя

# Локализация сообщений
LOCALIZATION = {
    "invalid_symbol": {
        "en": "Please provide a valid cryptocurrency symbol. Example: /price BTC",
        "ru": "Пожалуйста, укажите корректный символ криптовалюты. Пример: /price BTC"
    },
    "api_error": {
        "en": "Error fetching data. Please try again later.",
        "ru": "Ошибка получения данных. Пожалуйста, попробуйте позже."
    },
    "data_not_found": {
        "en": "No data found for this cryptocurrency.",
        "ru": "Данные по этой криптовалюте не найдены."
    }
}

# Функция для перевода сообщений
def translate(key, lang_code='en'):
    return LOCALIZATION.get(key, {}).get(lang_code, LOCALIZATION[key]['en'])

# Получение данных о цене криптовалюты
async def get_crypto_price(symbol):
    url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbol}&tsyms=USD,ETH&api_key={settings.crypto_api_key}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None  # Вернем None в случае неудачи запроса
                return await response.json()
    except aiohttp.ClientError as e:
        # Логируем ошибку и возвращаем None
        print(f"Ошибка при выполнении запроса: {e}")
        return None

# Форматирование сообщения о цене криптовалюты
async def format_crypto_message(data, symbol, lang_code='en'):
    try:
        display_data = data['DISPLAY'][symbol]['USD']

        # Изменения за 1 час и 24 часа в процентах и долларах
        change_hour = display_data.get('CHANGEHOUR', 'N/A')
        change_hour_percent = display_data.get('CHANGEPCTHOUR', 'N/A')
        change_day = display_data.get('CHANGE24HOUR', 'N/A')
        change_day_percent = display_data.get('CHANGEPCT24HOUR', 'N/A')
        btc_to_eth = data['DISPLAY'][symbol].get('ETH', {}).get('PRICE', 'N/A')

        if lang_code == 'ru':
            return (
                f"💰 {symbol} - USD\n"
                f"💲 Цена: {display_data['PRICE']}\n"
                f"💎 Макс/Мин (24ч): {display_data['HIGH24HOUR']} / {display_data['LOW24HOUR']}\n"
                f"⏳ Изменение за 1ч: {change_hour} USD ({change_hour_percent}%)\n"
                f"📈 Изменение за 24ч: {change_day} USD ({change_day_percent}%)\n"
                f"🏦 Рыночная капитализация: {display_data['MKTCAP']}\n"
                f"🔄 Объем за 24ч: {display_data['TOTALVOLUME24H']}\n"
                f"🪙 1 {symbol} = {btc_to_eth} ETH\n"
            )
        else:
            return (
                f"💰 {symbol} - USD\n"
                f"💲 Price: {display_data['PRICE']}\n"
                f"💎 H/L (24h): {display_data['HIGH24HOUR']} / {display_data['LOW24HOUR']}\n"
                f"⏳ 1h Change: {change_hour} USD ({change_hour_percent}%)\n"
                f"📈 24h Change: {change_day} USD ({change_day_percent}%)\n"
                f"🏦 Market Cap: {display_data['MKTCAP']}\n"
                f"🔄 24h Volume: {display_data['TOTALVOLUME24H']}\n"
                f"🪙 1 {symbol} = {btc_to_eth} ETH\n"
            )
    except KeyError:
        # Если данные не найдены или возникла ошибка при обработке
        return translate('data_not_found', lang_code)

# Обработчик команды /price
@dp.message(Command(commands=['price']))
async def send_price(message: Message):
    user_id = message.from_user.id
    # Получаем язык пользователя с помощью функции get_user_language
    lang_code = get_user_language(user_id)

    # Проверяем наличие символа криптовалюты в команде
    if len(message.text.split()) < 2:
        await message.reply(translate('invalid_symbol', lang_code))
        return

    symbol = message.text.split(' ')[1].upper()

    data = await get_crypto_price(symbol)

    # Проверка наличия данных
    if data is None:
        await message.reply(translate('api_error', lang_code))
        return

    if 'DISPLAY' not in data or symbol not in data['DISPLAY']:
        await message.reply(translate('invalid_symbol', lang_code))
        return

    # Форматируем сообщение и отправляем пользователю
    reply_message = await format_crypto_message(data, symbol, lang_code)
    await message.reply(reply_message)
