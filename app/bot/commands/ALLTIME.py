from binance import Client
import logging
from datetime import datetime
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from app.database.crud import get_user_language
from bot import dp
from config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация клиента Binance
binance_client = Client(api_key=settings.binance_api_key, api_secret=settings.binance_api_secret)

# Функция для получения исторических данных с Binance
def fetch_binance_ath(symbol, start_date='1 Jan, 2010'):
    logging.info(f"Получение исторических данных с Binance для {symbol} начиная с {start_date}")

    try:
        # Получение данных в виде свечей (kline)
        klines = binance_client.get_historical_klines(f"{symbol}USDT", Client.KLINE_INTERVAL_1DAY, start_date)
        return klines
    except Exception as e:
        logging.error(f"Ошибка при запросе данных с Binance для {symbol}: {e}")
        return None

# Функция для получения текущей цены криптовалюты
def fetch_binance_current_price(symbol):
    logging.info(f"Получение текущей цены для {symbol}")

    try:
        # Получение текущей цены через Binance API
        ticker = binance_client.get_symbol_ticker(symbol=f"{symbol}USDT")
        return float(ticker['price'])
    except Exception as e:
        logging.error(f"Ошибка при получении текущей цены для {symbol}: {e}")
        return None

# Функция для поиска наивысшей цены (ATH) в данных свечей
def find_all_time_high_binance(data):
    if not data:
        return None

    # Свечи возвращают следующие данные: [timestamp, open, high, low, close, ...]
    ath = max(data, key=lambda x: float(x[2]))  # x[2] - максимальная цена (high) в свечке
    return float(ath[2]), int(ath[0])  # Возвращаем наивысшую цену и timestamp

# Функция для преобразования времени из формата UNIX в читаемый формат дд.мм.гггг
def format_unix_timestamp(timestamp):
    date = datetime.utcfromtimestamp(timestamp / 1000)  # Binance возвращает время в миллисекундах
    return date.strftime('%d.%m.%Y')

# Обработчик команды /ath
@dp.message(Command(commands=['ath']))
async def send_all_time_high(message: Message):
    try:
        # Извлекаем символ криптовалюты из сообщения
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply("Пожалуйста, укажите символ криптовалюты. Например: /ath btc")
            return

        symbol = parts[1].upper()
        logging.info(f"Получение ATH для криптовалюты {symbol}")

        # Получаем исторические данные с Binance для поиска ATH
        crypto_data = fetch_binance_ath(symbol)

        if crypto_data:
            # Находим наивысшую цену за всю историю (ATH)
            ath_price, ath_time = find_all_time_high_binance(crypto_data)
            if ath_price:
                # Преобразуем время в формат дд.мм.гггг
                formatted_date = format_unix_timestamp(ath_time)

                # Получаем текущую цену
                current_price = fetch_binance_current_price(symbol)

                if current_price is not None:
                    # Вычисляем разницу между ATH и текущей ценой
                    difference = ath_price - current_price
                    percentage_diff = (difference / ath_price) * 100

                    # Получаем язык пользователя
                    user_language = get_user_language(message.from_user.id)

                    # Адаптация текста на основе языка пользователя
                    if user_language == "ru":
                        response_text = (
                            f"📈 <b>All Time High (ATH) для {symbol}:</b>\n\n"
                            f"💰 <b>Цена ATH:</b> ${ath_price}\n"
                            f"📅 <b>Дата:</b> {formatted_date}\n"
                            f"🏷️ <b>Текущая цена:</b> ${current_price}\n"
                            f"📉 <b>Разница:</b> ${difference:.2f} ({percentage_diff:.2f}%)"
                        )
                    else:
                        response_text = (
                            f"📈 <b>All Time High (ATH) for {symbol}:</b>\n\n"
                            f"💰 <b>ATH Price:</b> ${ath_price}\n"
                            f"📅 <b>Date:</b> {formatted_date}\n"
                            f"🏷️ <b>Current Price:</b> ${current_price}\n"
                            f"📉 <b>Difference:</b> ${difference:.2f} ({percentage_diff:.2f}%)"
                        )
                else:
                    response_text = f"Не удалось получить текущую цену для {symbol}."
            else:
                response_text = f"Не удалось найти ATH для {symbol}."
        else:
            response_text = f"Не удалось получить данные для {symbol}."

        # Отправляем ответ пользователю
        await message.reply(response_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Произошла ошибка при обработке команды /ath: {e}")
        await message.reply("Произошла ошибка при обработке команды.")
