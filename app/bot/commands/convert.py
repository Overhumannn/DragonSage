import random  # Для генерации случайных эмодзи 
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message  # Для обработки сообщений Telegram
from bot import dp  # Для доступа к диспетчеру вашего бота
from config import settings  # Для получения настроек, включая API ключи
from binance.client import Client  # Для взаимодействия с API Binance
from binance.exceptions import BinanceAPIException  # Для обработки исключений Binance
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя

binance_client = Client(settings.binance_api_key, settings.binance_api_secret)

# Получение списка доступных торговых пар при запуске бота
def get_available_symbols():
    exchange_info = binance_client.get_exchange_info()
    return {symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING'}

available_symbols = get_available_symbols()

@dp.message(Command(commands=['convert', 'конвертировать']))
async def convert_currency(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        language = get_user_language(message.from_user.id)  # Предполагается, что функция синхронная
        is_russian = (language == 'ru')

        # Извлекаем параметры команды
        args = message.text.split()
        if len(args) != 4:
            if is_russian:
                await message.reply(
                    "❗️ Пожалуйста, используйте команду в формате: /convert [from_symbol] [to_symbol] [amount]"
                )
            else:
                await message.reply(
                    "❗️ Please use the command in the format: /convert [from_symbol] [to_symbol] [amount]"
                )
            return

        from_symbol = args[1].upper()
        to_symbol = args[2].upper()
        try:
            amount = float(args[3])
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            if is_russian:
                await message.reply("❗️ Пожалуйста, укажите корректную положительную сумму для конвертации.")
            else:
                await message.reply("❗️ Please provide a valid positive amount for conversion.")
            return

        # Преобразуем символы в формат для API Binance (например, BTCUSDT)
        direct_pair = f"{from_symbol}{to_symbol}"
        indirect_pair_from = f"{from_symbol}USDT"
        indirect_pair_to = f"{to_symbol}USDT"

        # Проверяем наличие прямой пары
        if direct_pair in available_symbols:
            symbol_pair = direct_pair
            try:
                ticker = binance_client.get_symbol_ticker(symbol=symbol_pair)
                price = float(ticker['price'])
                converted_amount = amount * price
                conversion_type = 'direct'
            except BinanceAPIException as e:
                if e.code == -1121:
                    if is_russian:
                        await message.reply(
                            f"❌ Недопустимый символ: {symbol_pair}. Пожалуйста, проверьте правильность введённых символов."
                        )
                    else:
                        await message.reply(
                            f"❌ Invalid symbol: {symbol_pair}. Please check the symbols you entered."
                        )
                    return
                else:
                    if is_russian:
                        await message.reply("⚠️ Произошла ошибка при обращении к API Binance. Пожалуйста, попробуйте позже.")
                    else:
                        await message.reply("⚠️ An error occurred while communicating with Binance API. Please try again later.")
                    print(f"Binance API ошибка: {e}")
                    return
        else:
            # Если прямая пара недоступна, выполняем косвенную конвертацию через USDT
            if indirect_pair_from not in available_symbols:
                if is_russian:
                    await message.reply(
                        f"❌ Недопустимый символ: {indirect_pair_from}. Пожалуйста, проверьте правильность введённых символов."
                    )
                else:
                    await message.reply(
                        f"❌ Invalid symbol: {indirect_pair_from}. Please check the symbols you entered."
                    )
                return
            if indirect_pair_to not in available_symbols:
                if is_russian:
                    await message.reply(
                        f"❌ Недопустимый символ: {indirect_pair_to}. Пожалуйста, проверьте правильность введённых символов."
                    )
                else:
                    await message.reply(
                        f"❌ Invalid symbol: {indirect_pair_to}. Please check the symbols you entered."
                    )
                return

            try:
                # Получаем цену from_symbol в USDT
                ticker_from = binance_client.get_symbol_ticker(symbol=indirect_pair_from)
                price_from = float(ticker_from['price'])
                
                # Получаем цену to_symbol в USDT
                ticker_to = binance_client.get_symbol_ticker(symbol=indirect_pair_to)
                price_to = float(ticker_to['price'])
                
                # Конвертируем amount from_symbol в USDT, затем в to_symbol
                usdt_amount = amount * price_from
                converted_amount = usdt_amount / price_to
                conversion_type = 'indirect'
            except BinanceAPIException as e:
                if e.code == -1121:
                    if is_russian:
                        await message.reply(
                            f"❌ Недопустимый символ при косвенной конвертации. Пожалуйста, проверьте правильность введённых символов."
                        )
                    else:
                        await message.reply(
                            f"❌ Invalid symbol during indirect conversion. Please check the symbols you entered."
                        )
                    return
                else:
                    if is_russian:
                        await message.reply("⚠️ Произошла ошибка при обращении к API Binance. Пожалуйста, попробуйте позже.")
                    else:
                        await message.reply("⚠️ An error occurred while communicating with Binance API. Please try again later.")
                    print(f"Binance API ошибка: {e}")
                    return

        # Выбираем эмодзи для разнообразия
        conversion_emoji = random.choice(["💱", "🔄", "🔁"])
        rate_emoji = random.choice(["📉", "📈", "💵"])
        result_emoji = random.choice(["💰", "🏦", "💸"])

        # Формируем ответное сообщение
        if is_russian:
            if conversion_type == 'direct':
                response_message = (
                    f"{conversion_emoji} Конвертация {amount} {from_symbol} в {to_symbol}:\n"
                    f"{rate_emoji} Курс: 1 {from_symbol} = {price:.2f} {to_symbol}\n"
                    f"{result_emoji} Итоговая сумма: {converted_amount:.2f} {to_symbol}"
                )
            else:
                response_message = (
                    f"{conversion_emoji} Конвертация {amount} {from_symbol} в {to_symbol} через USDT:\n"
                    f"{rate_emoji} Курс {from_symbol}/USDT: {price_from:.2f} USDT\n"
                    f"{rate_emoji} Курс {to_symbol}/USDT: {price_to:.2f} USDT\n"
                    f"{result_emoji} Итоговая сумма: {converted_amount:.6f} {to_symbol}"
                )
        else:
            if conversion_type == 'direct':
                response_message = (
                    f"{conversion_emoji} Conversion of {amount} {from_symbol} to {to_symbol}:\n"
                    f"{rate_emoji} Rate: 1 {from_symbol} = {price:.2f} {to_symbol}\n"
                    f"{result_emoji} Total amount: {converted_amount:.2f} {to_symbol}"
                )
            else:
                response_message = (
                    f"{conversion_emoji} Conversion of {amount} {from_symbol} to {to_symbol} via USDT:\n"
                    f"{rate_emoji} {from_symbol}/USDT Rate: {price_from:.2f} USDT\n"
                    f"{rate_emoji} {to_symbol}/USDT Rate: {price_to:.2f} USDT\n"
                    f"{result_emoji} Total amount: {converted_amount:.6f} {to_symbol}"
                )

        await message.reply(response_message)

    except BinanceAPIException as e:
        # Дополнительная обработка исключений Binance, если необходимо
        if is_russian:
            await message.reply("⚠️ Произошла ошибка при обращении к API Binance. Пожалуйста, попробуйте позже.")
        else:
            await message.reply("⚠️ An error occurred while communicating with Binance API. Please try again later.")
        print(f"Binance API ошибка: {e}")
    except Exception as e:
        # В случае других ошибок отправляем сообщение на нужном языке
        if 'is_russian' in locals() and is_russian:
            await message.reply("⚠️ Произошла ошибка при попытке конвертации валют. Пожалуйста, попробуйте позже.")
        else:
            await message.reply("⚠️ An error occurred while trying to convert currencies. Please try again later.")
        print(f"Ошибка: {e}")
