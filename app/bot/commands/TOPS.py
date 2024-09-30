
from binance import Client  # Binance API
from aiogram import types
import aiohttp
from aiogram.filters import Command
from aiogram.types import Message
from config import settings
from bot import dp
import logging
import numpy as np  # Для расчетов RSI

# Настройка логирования 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dp.message(Command(commands=['cex_eth']))
async def top_ethereum_handler(message: Message):
    try:
        # Обновлённые эндпоинты Bitget API
        coins_url = "https://api.bitget.com/api/spot/v1/public/currencies"
        tickers_url = "https://api.bitget.com/api/spot/v1/market/tickers"
        headers = {'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            # Получаем список всех монет
            async with session.get(coins_url, headers=headers) as coins_response:
                logging.info(f"Статус ответа API (coins): {coins_response.status}")

                if coins_response.status == 200:
                    coins_data = await coins_response.json()
                    logging.debug(f"Тело ответа (coins): {coins_data}")

                    if 'data' not in coins_data or not coins_data['data']:
                        await message.reply("❗️Ошибка: Не удалось получить данные о монетах.")
                        return

                    coins = coins_data['data']

                    # Фильтруем монеты на Ethereum
                    eth_tokens = []
                    for coin in coins:
                        chains = coin.get('chains', [])
                        for chain_info in chains:
                            if chain_info.get('chain', '').upper() in ['ETH', 'ERC20', 'ETHEREUM']:
                                eth_tokens.append(coin['coinName'])
                                break  # Переходим к следующей монете

                    if not eth_tokens:
                        await message.reply("❗️Ошибка: Не удалось найти токены на блокчейне Ethereum.")
                        return

                    # Получаем данные о ценах и изменении за 24 часа
                    async with session.get(tickers_url, headers=headers) as tickers_response:
                        logging.info(f"Статус ответа API (tickers): {tickers_response.status}")

                        if tickers_response.status == 200:
                            tickers_data = await tickers_response.json()
                            logging.debug(f"Тело ответа (tickers): {tickers_data}")

                            if 'data' not in tickers_data or not tickers_data['data']:
                                await message.reply("❗️Ошибка: Не удалось получить данные о ценах.")
                                return

                            tickers = tickers_data['data']

                            # Создаем словарь тикеров для быстрого доступа
                            tickers_dict = {
                                item['symbol']: item for item in tickers
                            }

                            # Список для хранения данных о росте монет
                            growth_data = []

                            for symbol, ticker_info in tickers_dict.items():
                                # Проверяем, что символ заканчивается на USDT
                                if not symbol.endswith('USDT'):
                                    continue  # Пропускаем, если не USDT пара

                                # Извлекаем базовую валюту (токен)
                                token = symbol[:-4]  # Удаляем 'USDT' из конца символа

                                if token not in eth_tokens:
                                    continue  # Пропускаем токены, не относящиеся к Ethereum

                                last_price = float(ticker_info.get('close', 0))
                                open_price = float(ticker_info.get('openUtc0', 0)) or float(ticker_info.get('open24h', 0))

                                # Проверка и логирование цен
                                logging.debug(f"Токен: {token}, Symbol: {symbol}, Open Price: {open_price}, Last Price: {last_price}")

                                if open_price > 0:
                                    change_percent = ((last_price - open_price) / open_price) * 100
                                else:
                                    change_percent = 0

                                growth_data.append({
                                    'symbol': symbol,        # Полная торговая пара
                                    'token_name': token,     # Имя токена без USDT
                                    'last_price': last_price,
                                    'change_percent': change_percent
                                })

                            if not growth_data:
                                await message.reply("❗️Ошибка: Не удалось получить данные о росте токенов.")
                                return

                            # Сортируем по проценту роста
                            sorted_tokens = sorted(growth_data, key=lambda x: x['change_percent'], reverse=True)

                            # Формируем ответ с округленными значениями
                            title = f"🌟 <b>Топ наиболее быстрорастущих токенов на Ethereum за последние 24 часа:</b>\n\n"
                            response_text = title

                            # Базовый URL для Spot Trading на Bitget
                            base_url = "https://www.bitget.com/spot/"

                            for i, token_info in enumerate(sorted_tokens[:10], 1):  # Ограничиваем вывод 10 токенами
                                position_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐️"
                                symbol = token_info['symbol']          # Полная торговая пара (с USDT)
                                token_name = token_info['token_name']  # Имя токена без USDT
                                price = token_info['last_price']
                                change = token_info['change_percent']

                                # Формируем ссылку на торговую пару
                                trade_link = f"{base_url}{symbol}"

                                # Форматируем цену для избежания научной нотации
                                if price < 0.0001:
                                    price_str = f"{price:.8f}"
                                elif price < 0.01:
                                    price_str = f"{price:.6f}"
                                elif price < 1:
                                    price_str = f"{price:.4f}"
                                else:
                                    price_str = f"{price:.2f}"

                                # Форматируем процент изменения до двух знаков после запятой
                                change_str = f"{change:.2f}"

                                # Формируем ссылку с отображением только имени токена
                                response_text += (
                                    f"{position_emoji} <b><a href='{trade_link}'>{i}. {token_name}</a></b>\n"
                                    f"   💰 <b>Цена:</b> ${price_str}\n"
                                    f"   📈 <b>Рост за 24 часа:</b> {change_str}%\n\n"
                                )

                            # Отправляем ответ без отображения превью ссылок
                            await message.reply(response_text, parse_mode="HTML", disable_web_page_preview=True)

                        else:
                            error_data = await tickers_response.text()
                            logging.error(f"Ошибка запроса API (tickers): {error_data}")
                            await message.reply(f"❗️Ошибка: Не удалось получить данные о ценах. Статус: {tickers_response.status}")

                else:
                    error_data = await coins_response.text()
                    logging.error(f"Ошибка запроса API (coins): {error_data}")
                    await message.reply(f"❗️Ошибка: Не удалось получить данные о монетах. Статус: {coins_response.status}")

    except Exception as e:
        await message.reply("❗️Произошла ошибка при обработке запроса.")
        logging.error(f"Ошибка: {e}", exc_info=True)


@dp.message(Command(commands=['cex_sol']))
async def top_solana_handler(message: Message):
    try:
        # Обновлённые эндпоинты Bitget API
        coins_url = "https://api.bitget.com/api/spot/v1/public/currencies"
        tickers_url = "https://api.bitget.com/api/spot/v1/market/tickers"
        headers = {'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            # Получаем список всех монет
            async with session.get(coins_url, headers=headers) as coins_response:
                logging.info(f"Статус ответа API (coins): {coins_response.status}")

                if coins_response.status == 200:
                    coins_data = await coins_response.json()
                    logging.debug(f"Тело ответа (coins): {coins_data}")

                    if 'data' not in coins_data or not coins_data['data']:
                        await message.reply("❗️Ошибка: Не удалось получить данные о монетах.")
                        return

                    coins = coins_data['data']

                    # Фильтруем монеты на Solana
                    sol_tokens = []
                    for coin in coins:
                        chains = coin.get('chains', [])
                        for chain_info in chains:
                            if chain_info.get('chain', '').upper() in ['SOL', 'SOLANA']:
                                sol_tokens.append(coin['coinName'])
                                break  # Переходим к следующей монете

                    if not sol_tokens:
                        await message.reply("❗️Ошибка: Не удалось найти токены на блокчейне Solana.")
                        return

                    # Получаем данные о ценах и изменении за 24 часа
                    async with session.get(tickers_url, headers=headers) as tickers_response:
                        logging.info(f"Статус ответа API (tickers): {tickers_response.status}")

                        if tickers_response.status == 200:
                            tickers_data = await tickers_response.json()
                            logging.debug(f"Тело ответа (tickers): {tickers_data}")

                            if 'data' not in tickers_data or not tickers_data['data']:
                                await message.reply("❗️Ошибка: Не удалось получить данные о ценах.")
                                return

                            tickers = tickers_data['data']

                            # Создаем словарь тикеров для быстрого доступа
                            tickers_dict = {
                                item['symbol']: item for item in tickers
                            }

                            # Список для хранения данных о росте монет
                            growth_data = []

                            for symbol, ticker_info in tickers_dict.items():
                                # Проверяем, что символ заканчивается на USDT
                                if not symbol.endswith('USDT'):
                                    continue  # Пропускаем, если не USDT пара

                                # Извлекаем базовую валюту (токен)
                                token = symbol[:-4]  # Удаляем 'USDT' из конца символа

                                if token not in sol_tokens:
                                    continue  # Пропускаем токены, не относящиеся к Solana

                                last_price = float(ticker_info.get('close', 0))
                                open_price = float(ticker_info.get('openUtc0', 0)) or float(ticker_info.get('open24h', 0))

                                # Проверка и логирование цен
                                logging.debug(f"Токен: {token}, Symbol: {symbol}, Open Price: {open_price}, Last Price: {last_price}")

                                if open_price > 0:
                                    change_percent = ((last_price - open_price) / open_price) * 100
                                else:
                                    change_percent = 0

                                growth_data.append({
                                    'symbol': symbol,        # Полная торговая пара
                                    'token_name': token,     # Имя токена без USDT
                                    'last_price': last_price,
                                    'change_percent': change_percent
                                })

                            if not growth_data:
                                await message.reply("❗️Ошибка: Не удалось получить данные о росте токенов.")
                                return

                            # Сортируем по проценту роста
                            sorted_tokens = sorted(growth_data, key=lambda x: x['change_percent'], reverse=True)

                            # Формируем ответ с округленными значениями
                            title = f"🌟 <b>Топ наиболее быстрорастущих токенов на Solana за последние 24 часа:</b>\n\n"
                            response_text = title

                            # Базовый URL для Spot Trading на Bitget
                            base_url = "https://www.bitget.com/spot/"

                            for i, token_info in enumerate(sorted_tokens[:10], 1):  # Ограничиваем вывод 10 токенами
                                position_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐️"
                                symbol = token_info['symbol']          # Полная торговая пара (с USDT)
                                token_name = token_info['token_name']  # Имя токена без USDT
                                price = token_info['last_price']
                                change = token_info['change_percent']

                                # Формируем ссылку на торговую пару
                                trade_link = f"{base_url}{symbol}"

                                # Форматируем цену для избежания научной нотации
                                if price < 0.0001:
                                    price_str = f"{price:.8f}"
                                elif price < 0.01:
                                    price_str = f"{price:.6f}"
                                elif price < 1:
                                    price_str = f"{price:.4f}"
                                else:
                                    price_str = f"{price:.2f}"

                                # Форматируем процент изменения до двух знаков после запятой
                                change_str = f"{change:.2f}"

                                # Формируем ссылку с отображением только имени токена
                                response_text += (
                                    f"{position_emoji} <b><a href='{trade_link}'>{i}. {token_name}</a></b>\n"
                                    f"   💰 <b>Цена:</b> ${price_str}\n"
                                    f"   📈 <b>Рост за 24 часа:</b> {change_str}%\n\n"
                                )

                            # Отправляем ответ без отображения превью ссылок
                            await message.reply(response_text, parse_mode="HTML", disable_web_page_preview=True)

                        else:
                            error_data = await tickers_response.text()
                            logging.error(f"Ошибка запроса API (tickers): {error_data}")
                            await message.reply(f"❗️Ошибка: Не удалось получить данные о ценах. Статус: {tickers_response.status}")

                else:
                    error_data = await coins_response.text()
                    logging.error(f"Ошибка запроса API (coins): {error_data}")
                    await message.reply(f"❗️Ошибка: Не удалось получить данные о монетах. Статус: {coins_response.status}")

    except Exception as e:
        await message.reply("❗️Произошла ошибка при обработке запроса.")
        logging.error(f"Ошибка: {e}", exc_info=True)




@dp.message(Command(commands=['cex_ton']))
async def top_ton_handler(message: Message):
    try:
        # Обновлённые эндпоинты Bitget API
        coins_url = "https://api.bitget.com/api/spot/v1/public/currencies"
        tickers_url = "https://api.bitget.com/api/spot/v1/market/tickers"
        headers = {'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            # Получаем список всех монет
            async with session.get(coins_url, headers=headers) as coins_response:
                logging.info(f"Статус ответа API (coins): {coins_response.status}")

                if coins_response.status == 200:
                    coins_data = await coins_response.json()
                    logging.debug(f"Тело ответа (coins): {coins_data}")

                    if 'data' not in coins_data or not coins_data['data']:
                        await message.reply("❗️Ошибка: Не удалось получить данные о монетах.")
                        return

                    coins = coins_data['data']

                    # Фильтруем монеты на блокчейне TON
                    ton_tokens = []
                    for coin in coins:
                        chains = coin.get('chains', [])
                        for chain_info in chains:
                            if chain_info.get('chain', '').upper() in ['TON', 'TONCOIN']:
                                ton_tokens.append(coin['coinName'] if coin['coinName'] != "TONCOIN" else "TON")
                                break  # Переходим к следующей монете

                    if not ton_tokens:
                        await message.reply("❗️Ошибка: Не удалось найти токены на блокчейне TON.")
                        return

                    # Получаем данные о ценах и изменении за 24 часа
                    async with session.get(tickers_url, headers=headers) as tickers_response:
                        logging.info(f"Статус ответа API (tickers): {tickers_response.status}")

                        if tickers_response.status == 200:
                            tickers_data = await tickers_response.json()
                            logging.debug(f"Тело ответа (tickers): {tickers_data}")

                            if 'data' not in tickers_data or not tickers_data['data']:
                                await message.reply("❗️Ошибка: Не удалось получить данные о ценах.")
                                return

                            tickers = tickers_data['data']

                            # Создаем словарь тикеров для быстрого доступа
                            tickers_dict = {
                                item['symbol']: item for item in tickers
                            }

                            # Список для хранения данных о росте монет
                            growth_data = []

                            for symbol, ticker_info in tickers_dict.items():
                                # Проверяем, что символ заканчивается на USDT
                                if not symbol.endswith('USDT'):
                                    continue  # Пропускаем, если не USDT пара

                                # Извлекаем базовую валюту (токен)
                                token = symbol[:-4]  # Удаляем 'USDT' из конца символа

                                if token not in ton_tokens:
                                    continue  # Пропускаем токены, не относящиеся к блокчейну TON

                                # Обрабатываем случай, когда токен "TONCOIN" меняется на "TON"
                                if token == "TONCOIN":
                                    token = "TON"

                                last_price = float(ticker_info.get('close', 0))
                                open_price = float(ticker_info.get('openUtc0', 0)) or float(ticker_info.get('open24h', 0))

                                # Проверка и логирование цен
                                logging.debug(f"Токен: {token}, Symbol: {symbol}, Open Price: {open_price}, Last Price: {last_price}")

                                if open_price > 0:
                                    change_percent = ((last_price - open_price) / open_price) * 100
                                else:
                                    change_percent = 0

                                growth_data.append({
                                    'symbol': symbol if token != "TON" else "TONUSDT",  # Устанавливаем символ TONUSDT
                                    'token_name': token,     # Имя токена без USDT
                                    'last_price': last_price,
                                    'change_percent': change_percent
                                })

                            if not growth_data:
                                await message.reply("❗️Ошибка: Не удалось найти токены с изменением.")
                                return

                            # Сортируем по проценту роста
                            sorted_tokens = sorted(growth_data, key=lambda x: x['change_percent'], reverse=True)

                            # Формируем ответ с округленными значениями
                            title = f"🌟 <b>Топ наиболее быстрорастущих токенов на TON за последние 24 часа:</b>\n\n"
                            response_text = title

                            # Базовый URL для Spot Trading на Bitget
                            base_url = "https://www.bitget.com/spot/"

                            for i, token_info in enumerate(sorted_tokens[:10], 1):  # Ограничиваем вывод 10 токенами
                                position_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐️"
                                symbol = token_info['symbol']          # Полная торговая пара (с USDT)
                                token_name = token_info['token_name']  # Имя токена без USDT
                                price = token_info['last_price']
                                change = token_info['change_percent']

                                # Формируем ссылку на торговую пару
                                trade_link = f"{base_url}{symbol}"

                                # Форматируем цену для избежания научной нотации
                                if price < 0.0001:
                                    price_str = f"{price:.8f}"
                                elif price < 0.01:
                                    price_str = f"{price:.6f}"
                                elif price < 1:
                                    price_str = f"{price:.4f}"
                                else:
                                    price_str = f"{price:.2f}"

                                # Форматируем процент изменения до двух знаков после запятой
                                change_str = f"{change:.2f}"

                                # Формируем ссылку с отображением только имени токена
                                response_text += (
                                    f"{position_emoji} <b><a href='{trade_link}'>{i}. {token_name}</a></b>\n"
                                    f"   💰 <b>Цена:</b> ${price_str}\n"
                                    f"   📈 <b>Рост за 24 часа:</b> {change_str}%\n\n"
                                )

                            # Отправляем ответ без отображения превью ссылок
                            await message.reply(response_text, parse_mode="HTML", disable_web_page_preview=True)

                        else:
                            error_data = await tickers_response.text()
                            logging.error(f"Ошибка запроса API (tickers): {error_data}")
                            await message.reply(f"❗️Ошибка: Не удалось получить данные о ценах. Статус: {tickers_response.status}")

                else:
                    error_data = await coins_response.text()
                    logging.error(f"Ошибка запроса API (coins): {error_data}")
                    await message.reply(f"❗️Ошибка: Не удалось получить данные о монетах. Статус: {coins_response.status}")

    except Exception as e:
        await message.reply("❗️Произошла ошибка при обработке запроса.")
        logging.error(f"Ошибка: {e}", exc_info=True)












