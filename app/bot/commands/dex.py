import logging
import random
import aiohttp
from datetime import datetime, timedelta
import requests

from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message

from app.database.crud import get_user_language
from bot import dp  # Ваш экземпляр Dispatcher
from config import settings

# Настройка логирования
logger = logging.getLogger(__name__)

# Сообщения для разных языков с эмодзи
messages = {
    'en': {
        'no_symbol': [
            "❗ Please specify a cryptocurrency symbol. For example: /dex BTC",
            "🔍 Please provide a crypto symbol. Example: /dex BTC",
            "🤔 What crypto are you interested in? For example: /dex BTC"
        ],
        'price': [
            "💰 The price of {symbol} is {price} USDT.",
            "📈 {symbol} is currently trading at {price} USDT.",
            "💹 {symbol} price: {price} USDT."
        ],
        'error': [
            "⚠️ Error: {error_message}",
            "❌ Error: {error_message}",
            "🚫 Error: {error_message}"
        ],
        'unknown_error': [
            "❓ Could not retrieve the price. Please try again later.",
            "😕 Couldn't get the price. Try again later.",
            "🔄 Unable to fetch the price at this time. Please try again."
        ],
        'api_error': [
            "🔧 Failed to retrieve data from CryptoCompare API.",
            "🛠️ API Error: Unable to get data from CryptoCompare.",
            "📡 Could not connect to CryptoCompare API."
        ],
        'wbtc_info': [
            "ℹ️ Note: On DEX platforms like Uniswap, BTC is often represented as WBTC (Wrapped BTC). Using WBTC for price queries.",
            "📝 Note: BTC is represented as WBTC on DEX platforms like Uniswap. Using WBTC for price queries.",
            "🔍 Note: On DEXs such as Uniswap, BTC is usually WBTC (Wrapped BTC). Using WBTC for price queries."
        ]
    },
    'ru': {
        'no_symbol': [
            "❗ Пожалуйста, укажите символ криптовалюты. Например: /dex BTC",
            "🔍 Пожалуйста, предоставьте символ криптовалюты. Пример: /dex BTC",
            "🤔 Какую криптовалюту вы хотите узнать? Например: /dex BTC"
        ],
        'price': [
            "💰 Цена {symbol} составляет {price} USDT.",
            "📈 {symbol} сейчас торгуется по {price} USDT.",
            "💹 Цена {symbol}: {price} USDT."
        ],
        'error': [
            "⚠️ Ошибка: {error_message}",
            "❌ Ошибка: {error_message}",
            "🚫 Ошибка: {error_message}"
        ],
        'unknown_error': [
            "❓ Не удалось получить цену. Пожалуйста, попробуйте позже.",
            "😕 Не удалось получить цену. Попробуйте позже.",
            "🔄 Не удалось получить цену в данный момент. Пожалуйста, попробуйте снова."
        ],
        'api_error': [
            "🔧 Не удалось получить данные от CryptoCompare API.",
            "🛠️ Ошибка API: Не удалось получить данные от CryptoCompare.",
            "📡 Не удалось подключиться к CryptoCompare API."
        ],
        'wbtc_info': [
            "ℹ️ Примечание: На DEX-платформах, таких как Uniswap, BTC часто представлен как WBTC (Wrapped BTC). Используется WBTC для запросов цен.",
            "📝 Примечание: BTC представлен как WBTC на DEX-платформах, таких как Uniswap. Используется WBTC для запросов цен.",
            "🔍 Примечание: На DEX, таких как Uniswap, BTC обычно представлен как WBTC (Wrapped BTC). Используется WBTC для запросов цен."
        ]
    },
    # Добавьте другие языки, если необходимо
}

@dp.message(Command('dex'))
async def dex_command_handler(message: Message):
    logger.info(f"Received /dex command from user {message.from_user.id}")

    try:
        # Получаем предпочтительный язык пользователя
        user_language = get_user_language(message.from_user.id)
        logger.debug(f"User language: {user_language}")
    except Exception as e:
        logger.error(f"Error fetching user language: {e}")
        user_language = 'en'  # По умолчанию

    # По умолчанию используем английский, если язык не поддерживается
    lang = messages.get(user_language, messages['en'])

    # Получаем символ криптовалюты из текста сообщения
    args = message.text.strip().split()
    if len(args) < 2:
        logger.warning(f"No symbol provided by user {message.from_user.id}")
        response = random.choice(lang['no_symbol'])
        await message.reply(response)
        return

    symbol = args[1].upper()
    logger.info(f"Fetching price for symbol: {symbol}")

    # Проверяем, если символ BTC, заменяем его на WBTC
    if symbol == 'BTC':
        symbol = 'WBTC'
        logger.info("Symbol BTC detected. Using WBTC for query.")
        response = random.choice(lang['wbtc_info'])
        await message.reply(response)

    # Подготавливаем запрос к API без указания биржи
    url = 'https://min-api.cryptocompare.com/data/price'
    params = {
        'fsym': symbol,
        'tsyms': 'USDT',
        'api_key': settings.crypto_api_key  # Исправлено имя атрибута
        # 'e': exchange  # Удалено
    }
    logger.debug(f"API request URL: {url} with params: {params}")

    try:
        # Делаем запрос к API
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                logger.debug(f"API response status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    logger.debug(f"API response data: {data}")
                    if 'USDT' in data:
                        price = data['USDT']
                        logger.info(f"Price fetched: {symbol} = {price} USDT")
                        response = random.choice(lang['price']).format(symbol=symbol, price=price)
                        await message.reply(response)
                    elif 'Response' in data and data['Response'] == 'Error':
                        error_message = data.get('Message', 'Unknown error.')
                        logger.error(f"API Error: {error_message}")
                        response = random.choice(lang['error']).format(error_message=error_message)
                        await message.reply(response)
                    else:
                        logger.warning("Unknown API response structure.")
                        response = random.choice(lang['unknown_error'])
                        await message.reply(response)
                else:
                    logger.error(f"API request failed with status {resp.status}")
                    response = random.choice(lang['api_error'])
                    await message.reply(response)
    except Exception as e:
        logger.exception(f"Exception during API request: {e}")
        response = random.choice(lang['unknown_error'])
        await message.reply(response)










# Настройка логирования
logger = logging.getLogger(__name__)

# Список уникальных эмодзи для топ-10 токенов
token_emojis = [
    "🔥", "🌟", "🚀", "💎", "⚡️", "📈", "🌈", "🛡️", "💰", "🎯"
]

# Сообщения для разных языков с эмодзи
messages = {
    'en': {
        'no_data': [
            "😔 No data available at the moment. Please try again later.",
            "📉 Unable to retrieve data currently. Try again later.",
            "🔄 Data is not available right now. Please try again."
        ],
        'top_tokens': [
            "🚀 Top {limit} Fastest Growing Tokens on Uniswap in the Ethereum network:\n",
            "📈 Top {limit} Rapidly Rising Tokens on Uniswap in the Ethereum network:\n",
            "💹 Top {limit} High-Growth Tokens on Uniswap in the Ethereum network:\n"
        ],
        'token_format': "{rank}. {emoji} {symbol} ({name}) - ${price:.6f} (+{change:.2f}% in 24h)\n",
        'error': [
            "⚠️ Error: {error_message}",
            "❌ Error: {error_message}",
            "🚫 Error: {error_message}"
        ],
        'unknown_error': [
            "❓ Could not retrieve the data. Please try again later.",
            "😕 Couldn't get the data. Try again later.",
            "🔄 Unable to fetch the data at this time. Please try again."
        ],
        'api_error': [
            "🔧 Failed to retrieve data from The Graph API.",
            "🛠️ API Error: Unable to get data from The Graph.",
            "📡 Could not connect to The Graph API."
        ],
    },
    'ru': {
        'no_data': [
            "😔 Нет доступных данных в данный момент. Пожалуйста, попробуйте позже.",
            "📉 Не удалось получить данные. Попробуйте позже.",
            "🔄 Данные недоступны сейчас. Пожалуйста, попробуйте снова."
        ],
        'top_tokens': [
            "🚀 ТОП {limit} наиболее быстрорастущих токенов на Uniswap в сети Ethereum:\n",
            "📈 ТОП {limit} быстрорастущих токенов на Uniswap в сети Ethereum:\n",
            "💹 ТОП {limit} токенов с высоким ростом на Uniswap в сети Ethereum:\n"
        ],
        'token_format': "{rank}. {emoji} {symbol} ({name}) - ${price:.6f} (+{change:.2f}% за 24ч)\n",
        'error': [
            "⚠️ Ошибка: {error_message}",
            "❌ Ошибка: {error_message}",
            "🚫 Ошибка: {error_message}"
        ],
        'unknown_error': [
            "❓ Не удалось получить данные. Пожалуйста, попробуйте позже.",
            "😕 Не удалось получить данные. Попробуйте позже.",
            "🔄 Не удалось получить данные в данный момент. Пожалуйста, попробуйте снова."
        ],
        'api_error': [
            "🔧 Не удалось получить данные от The Graph API.",
            "🛠️ Ошибка API: Не удалось получить данные от The Graph.",
            "📡 Не удалось подключиться к The Graph API."
        ],
    },
    # Добавьте другие языки, если необходимо
}

@dp.message(Command('dex_eth'))
async def dex_eth_command_handler(message: Message):
    logger.info(f"Received /dex_eth command from user {message.from_user.id}")

    try:
        # Получаем предпочтительный язык пользователя
        user_language = get_user_language(message.from_user.id)
        logger.debug(f"User language: {user_language}")
    except Exception as e:
        logger.error(f"Error fetching user language: {e}")
        user_language = 'en'  # По умолчанию

    # По умолчанию используем английский, если язык не поддерживается
    lang = messages.get(user_language, messages['en'])

    limit = 10  # Количество токенов в ТОПе

    # Вычисляем метки времени для сегодняшнего и вчерашнего дня
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)

    try:
        today_date = datetime(today.year, today.month, today.day)
        yesterday_date = datetime(yesterday.year, yesterday.month, yesterday.day)

        today_timestamp = int(today_date.timestamp())
        yesterday_timestamp = int(yesterday_date.timestamp())

        logger.debug(f"Timestamps - Today: {today_timestamp}, Yesterday: {yesterday_timestamp}")
    except Exception as e:
        logger.error(f"Error processing dates: {e}")
        response = random.choice(lang['unknown_error'])
        await message.reply(response)
        return

    # GraphQL запрос к субграфу Uniswap на Arbitrum
    graphql_query = """
    {
      tokens(first: 100, orderBy: totalValueLockedUSD, orderDirection: desc) {
        id
        symbol
        name
        totalValueLockedUSD
        tokenDayData(first: 2, orderBy: date, orderDirection: desc) {
          date
          priceUSD
        }
      }
    }
    """

    # Используем предоставленный URL и API-ключ
    api_key = settings.thegraph_api_key
    subgraph_id = '5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV'

    url = f'https://gateway.thegraph.com/api/{api_key}/subgraphs/id/{subgraph_id}'

    logger.debug(f"GraphQL endpoint URL: {url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'query': graphql_query}) as resp:
                logger.debug(f"GraphQL response status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    tokens = data.get('data', {}).get('tokens', [])
                    logger.debug(f"Fetched {len(tokens)} tokens")

                    token_changes = []

                    for token in tokens:
                        token_day_data = token.get('tokenDayData', [])
                        if len(token_day_data) >= 2:
                            today_data = token_day_data[0]
                            yesterday_data = token_day_data[1]

                            price_today = float(today_data.get('priceUSD', 0))
                            price_yesterday = float(yesterday_data.get('priceUSD', 0))

                            if price_yesterday > 0 and price_today > 0:
                                price_change = ((price_today - price_yesterday) / price_yesterday) * 100
                                token_changes.append({
                                    'symbol': token.get('symbol'),
                                    'name': token.get('name'),
                                    'price': price_today,
                                    'change': price_change
                                })
                                logger.debug(f"{token.get('symbol')}: Price Today = {price_today}, Price Yesterday = {price_yesterday}, Change = {price_change}%")

                    # Сортируем токены по процентному изменению цены
                    sorted_tokens = sorted(token_changes, key=lambda x: x['change'], reverse=True)

                    if not sorted_tokens:
                        response = random.choice(lang['no_data'])
                        await message.reply(response)
                        return

                    top_tokens = sorted_tokens[:limit]
                    header = random.choice(lang['top_tokens']).format(limit=limit)
                    token_list = ""
                    for idx, token in enumerate(top_tokens, start=1):
                        emoji = token_emojis[idx - 1] if idx - 1 < len(token_emojis) else ''
                        token_list += lang['token_format'].format(
                            rank=idx,
                            emoji=emoji,
                            symbol=token['symbol'],
                            name=token['name'],
                            price=token['price'],
                            change=token['change']
                        )

                    response = header + token_list
                    await message.reply(response)
                else:
                    error_text = await resp.text()
                    logger.error(f"GraphQL request failed with status {resp.status}: {error_text}")
                    response = random.choice(lang['api_error'])
                    await message.reply(response)
    except Exception as e:
        logger.exception(f"Exception during GraphQL request: {e}")
        response = random.choice(lang['unknown_error'])
        await message.reply(response)














# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Эмодзи для топ-10 токенов
token_emojis = [
    "🔥", "🌟", "🚀", "💎", "⚡️", "📈", "🌈", "🛡️", "💰", "🎯"
]

# Сообщения для разных языков
messages = {
    'en': {
        'no_data': "😔 No data available at the moment. Please try again later.",
        'top_tokens': "🚀 Top {limit} Fastest Growing Tokens on Tron DEX:\n",
        'token_format': "{rank}. {emoji} {symbol} ({name}) - ${price:.6f} ({change:+.2f}% in 24h)\n",
        'error': "⚠️ Error: {error_message}",
    },
    'ru': {
        'no_data': "😔 Нет доступных данных в данный момент. Пожалуйста, попробуйте позже.",
        'top_tokens': "🚀 ТОП {limit} наиболее быстрорастущих токенов на Tron DEX:\n",
        'token_format': "{rank}. {emoji} {symbol} ({name}) - ${price:.6f} ({change:+.2f}% за 24ч)\n",
        'error': "⚠️ Ошибка: {error_message}",
    }
}

@dp.message(Command('dex_tron'))
async def dex_tron_command_handler(message: types.Message):
    logger.info(f"Received /dex_tron command from user {message.from_user.id}")

    lang = messages.get('ru')

    # URL API для получения топ-10 наиболее быстрорастущих токенов на Tron
    url = "https://apilist.tronscanapi.com/api/tokens/overview"
    params = {
        "start": 0,
        "limit": 500,   # Максимальный лимит для получения всех токенов
        "order": "desc",  # В порядке убывания
        "filter": "all",  # Включаем все типы токенов
        "sort": "gain",   # Сортировка по приросту
        "showAll": 1,     # Возвращаем все токены, включая черный список
        "verifier": "all",
        "field": ""
    }

    headers = {
        "Accept": "application/json",
        "TRON-PRO-API-KEY": settings.tron_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            logger.debug(f"Requesting URL: {url} with params: {params} and headers: {headers}")
            async with session.get(url, params=params, headers=headers) as resp:
                logger.debug(f"Received response with status code: {resp.status}")
                text = await resp.text()
                logger.debug(f"Response text: {text}")  # Логируем полный текст ответа
                if resp.status != 200:
                    raise Exception(
                        f"Unexpected status code: {resp.status}, response: {text}"
                    )
                data = await resp.json()
                tokens = data.get('tokens', [])
                logger.info(f"Fetched {len(tokens)} tokens from TronScan API")

        # Если токенов нет, выводим сообщение
        if not tokens:
            await message.reply(lang['no_data'])
            return

        # Формируем список токенов с положительным приростом
        token_changes = []
        for token in tokens:
            price_in_usd = token.get('priceInUsd')
            gain = token.get('gain')
            symbol = token.get('abbr', 'N/A')
            name = token.get('name', 'N/A')

            logger.debug(f"Token: {symbol}, Gain: {gain}, Price: {price_in_usd}")

            if gain is not None and price_in_usd is not None:
                try:
                    gain_value = float(gain)
                    price = float(price_in_usd)
                    # Предполагаем, что 'gain' уже представляет процентное изменение за 24 часа
                    # Если 'gain' - это десятичная дробь, умножаем на 100
                    change = gain_value * 100 if abs(gain_value) < 100 else gain_value
                    # Фильтруем токены с положительным приростом
                    if change > 0:
                        token_changes.append({
                            'symbol': symbol,
                            'name': name,
                            'price': price,
                            'change': change
                        })
                except ValueError as e:
                    logger.debug(f"Error parsing price or gain for token {symbol}: {e}")
                    continue

        logger.info(f"Tokens with valid gain and price: {len(token_changes)}")

        if not token_changes:
            await message.reply(lang['no_data'])
            return

        # Сортировка по изменению цены за 24 часа
        sorted_tokens = sorted(token_changes, key=lambda x: x['change'], reverse=True)

        # Получаем топ-10 токенов с наибольшим ростом
        top_tokens = sorted_tokens[:10]

        logger.info(f"Top tokens selected: {len(top_tokens)}")

        # Формируем ответ
        token_list = ""
        for idx, token in enumerate(top_tokens, start=1):
            emoji = token_emojis[idx - 1] if idx - 1 < len(token_emojis) else ''
            token_list += lang['token_format'].format(
                rank=idx,
                emoji=emoji,
                symbol=token['symbol'],
                name=token['name'],
                price=token['price'],
                change=token['change']
            )

        response_message = lang['top_tokens'].format(limit=10) + token_list
        await message.reply(response_message)

    except aiohttp.ClientError as e:
        logger.error(f"API request error: {e}")
        await message.reply(lang['error'].format(error_message="Ошибка запроса к API"))
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        await message.reply(lang['error'].format(error_message="Неожиданная ошибка"))