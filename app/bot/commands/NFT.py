import aiohttp
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from config import settings  # Здесь хранится ваш API-ключ
from bot import dp  # Импорт диспетчера из основного файла
import requests
from app.database.crud import get_user_language
import logging
from datetime import datetime


# Функция для форматирования чисел с ограничением до 5 знаков после запятой
def format_number(number):
    return f"{number:.4f}"


# Функция для получения текста на основе языка пользователя
def get_text(language, key):
    texts = {
        'en': {
            'title': "🤖 Detailed statistics for the collection",
            'volume': "💰 Total sales volume:",
            'sales': "🛒 Total sales:",
            'average_price': "📊 Average sale price:",
            'owners': "👥 Number of owners:",
            'market_cap': "💎 Market capitalization:",
            'floor_price': "📉 Floor price:",
            'periods': "📅 Period data:",
            'volume_period': "📈 Sales volume:",
            'sales_period': "🛒 Sales:",
            'volume_change': "⚖️ Volume change:",
            'sales_change': "💸 Sales change:",
            'collection_not_found': "❗️Collection not found. Check the slug.",
            'api_error': "❗️Error: Failed to retrieve data from the OpenSea API.",
            'client_error': "❗️An error occurred while retrieving data."
        },
        'ru': {
            'title': "🤖 Подробная статистика коллекции",
            'volume': "💰 Общий объем продаж:",
            'sales': "🛒 Общее количество продаж:",
            'average_price': "📊 Средняя цена продажи:",
            'owners': "👥 Количество владельцев:",
            'market_cap': "💎 Рыночная капитализация:",
            'floor_price': "📉 Минимальная цена:",
            'periods': "📅 Данные по периодам:",
            'volume_period': "📈 Объем продаж:",
            'sales_period': "🛒 Продажи:",
            'volume_change': "⬆️ Изменение объема:",
            'sales_change': "⬆️ Изменение продаж:",
            'collection_not_found': "❗️Коллекция не найдена. Проверьте правильность введенного slug.",
            'api_error': "❗️Ошибка: Не удалось получить данные от API OpenSea.",
            'client_error': "❗️Произошла ошибка при получении данных."
        }
    }
    return texts[language][key]


# Функция для добавления эмодзи на основе изменения
def add_emoji_for_change(value):
    if value > 0:
        return f"💚 {format_number(value)}%"
    elif value < 0:
        return f"💔 {format_number(value)}%"
    else:
        return f"{format_number(value)}%"


# Обработчик команды /nft
@dp.message(Command(commands=['nft']))
async def nft_info_handler(message: Message):
    # Получаем коллекцию из текста сообщения
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply("Please specify the collection name after the /nft command.")
        return

    user_id = message.from_user.id

    # Получаем язык пользователя из базы данных
    language = get_user_language(user_id)

    collection_slug = text[1].strip().lower()
    stats_url = f"https://api.opensea.io/api/v2/collections/{collection_slug}/stats"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Получаем статистику коллекции
            async with session.get(stats_url, headers=headers) as response:
                status_code = response.status
                response_text = await response.text()
                print(f"Status: {status_code}")
                print(f"Response: {response_text}")

                if status_code == 200:
                    data = await response.json()
                    total_stats = data.get('total', {})
                    intervals = data.get('intervals', [])

                    if total_stats:
                        response_text = (
                            f"{get_text(language, 'title')} {collection_slug}:\n\n"
                            f"{get_text(language, 'volume')} {format_number(total_stats.get('volume', 0))} ETH\n"
                            f"{get_text(language, 'sales')} {total_stats.get('sales', 0)}\n"
                            f"{get_text(language, 'average_price')} {format_number(total_stats.get('average_price', 0))} ETH\n"
                            f"{get_text(language, 'owners')} {total_stats.get('num_owners', 0)}\n"
                            f"{get_text(language, 'market_cap')} {format_number(total_stats.get('market_cap', 0))} ETH\n"
                            f"{get_text(language, 'floor_price')} {format_number(total_stats.get('floor_price', 0))} {total_stats.get('floor_price_symbol', 'ETH')}\n"
                        )
                    else:
                        response_text = get_text(language, 'collection_not_found')

                    if intervals:
                        response_text += f"\n{get_text(language, 'periods')}\n"
                        for interval in intervals:
                            interval_name = interval['interval'].replace('_', ' ').title()
                            volume_change = interval.get('volume_diff', 0) / interval['volume'] * 100 if interval[
                                'volume'] else 0
                            sales_change = interval.get('sales_diff', 0) / interval['sales'] * 100 if interval[
                                'sales'] else 0

                            response_text += (
                                f"🔹 <b>{interval_name}:</b>\n"
                                f"   {get_text(language, 'volume_period')} {format_number(interval['volume'])} ETH\n"
                                f"   {get_text(language, 'sales_period')} {interval['sales']}\n"
                                f"   {get_text(language, 'volume_change')} {add_emoji_for_change(volume_change)}\n"
                            )

                            if sales_change != 0:
                                response_text += f"   {get_text(language, 'sales_change')} {add_emoji_for_change(sales_change)}\n"

                            response_text += "\n"

                elif status_code == 404:
                    response_text = get_text(language, 'collection_not_found')
                else:
                    response_text = f"{get_text(language, 'api_error')} Статус: {status_code}."

        # Отправляем сообщение пользователю
        await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply(get_text(language, 'client_error'))
        print(f"Ошибка запроса: {e}")

    except Exception as e:
        await message.reply(get_text(language, 'client_error'))
        print(f"Ошибка: {e}")


@dp.message(Command(commands=['nft_events']))
async def nft_events_handler(message: Message):
    # Получаем язык пользователя из базы данных
    user_language = get_user_language(message.from_user.id)

    # Устанавливаем язык сообщений на основе данных из базы
    if user_language == 'ru':
        recent_events_text = "🤖 <b>Последние события на OpenSea:</b>\n\n"
        link_text = "🔗 <b>Ссылка:</b>"
        price_text = "💰 <b>Цена:</b>"
        event_type_text = "🔄 <b>Тип события:</b>"
        chain_text = "🌐 <b>Сеть:</b>"
        not_found_text = "❗️Не найдено недавних событий на OpenSea."
        error_text = "❗️Ошибка: Не удалось получить данные от API OpenSea. Статус: {}."
        client_error_text = "❗️Произошла ошибка при получении данных."
        unexpected_error_text = "❗️Произошла непредвиденная ошибка."
        no_name_text = "🖼️ Без имени"
    else:
        recent_events_text = "🤖 <b>Recent events on OpenSea:</b>\n\n"
        link_text = "🔗 <b>Link:</b>"
        price_text = "💰 <b>Price:</b>"
        event_type_text = "🔄 <b>Event Type:</b>"
        chain_text = "🌐 <b>Chain:</b>"
        not_found_text = "❗️No recent events found on OpenSea."
        error_text = "❗️Error: Failed to fetch data from OpenSea API. Status: {}."
        client_error_text = "❗️There was an error fetching the data."
        unexpected_error_text = "❗️An unexpected error occurred."
        no_name_text = "🖼️ No Name"

    # Получаем параметры команды
    args = message.text.split()[1:]  # Получаем все аргументы после команды
    args = ' '.join(args).replace(',', ' ').split()  # Убираем запятые и делаем список параметров

    # Разбираем параметры
    params = {
        "event_type": "sale",  # По умолчанию фильтруем только продажи
        "only_opensea": "false",
        "offset": "0",
        "limit": "20"  # Устанавливаем максимальный лимит
    }

    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            params[key.strip()] = value.strip()

    url = "https://api.opensea.io/api/v2/events"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                status_code = response.status
                if status_code == 200:
                    data = await response.json()
                    events = data.get('asset_events', [])

                    if events:
                        response_text = recent_events_text
                        for event in events:
                            nft_data = event.get('nft', {})
                            asset_name = nft_data.get('name', no_name_text)
                            asset_url = nft_data.get('opensea_url', '#')
                            payment_data = event.get('payment', {})
                            total_price = float(payment_data.get('quantity', 0)) / (10 ** payment_data.get('decimals', 18))
                            payment_token = payment_data.get('symbol', 'ETH')
                            chain = event.get('chain', 'ethereum').capitalize()
                            event_type = event.get('event_type', 'Sale').capitalize()

                            response_text += (
                                f"🔹 <b>{asset_name}</b>\n"
                                f"{link_text} <a href='{asset_url}'>OpenSea</a>\n"
                                f"{price_text} {total_price:.5f} {payment_token}\n"
                                f"{event_type_text} {event_type}\n"
                                f"{chain_text} {chain}\n\n"
                            )
                    else:
                        response_text = not_found_text

                else:
                    response_text = error_text.format(status_code)

        await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply(client_error_text)
        print(f"Ошибка запроса: {e}")

    except Exception as e:
        await message.reply(unexpected_error_text)
        print(f"Ошибка: {e}")




@dp.message(Command(commands=['nft_events_collection']))
async def nft_events_collection_handler(message: Message):
    # Получаем язык пользователя из базы данных
    user_language = get_user_language(message.from_user.id)

    # Устанавливаем язык сообщений на основе данных из базы
    if user_language == 'ru':
        recent_events_text = "🤖 <b>Последние события коллекции на OpenSea:</b>\n\n"
        link_text = "🔗 <b>Ссылка:</b>"
        price_text = "💰 <b>Цена:</b>"
        event_type_text = "🔄 <b>Тип события:</b>"
        chain_text = "🌐 <b>Сеть:</b>"
        not_found_text = "❗️Не найдено недавних событий коллекции на OpenSea."
        error_text = "❗️Ошибка: Не удалось получить данные от API OpenSea. Статус: {}."
        client_error_text = "❗️Произошла ошибка при получении данных."
        unexpected_error_text = "❗️Произошла непредвиденная ошибка."
        no_name_text = "🖼️ Без имени"
    else:
        recent_events_text = "🤖 <b>Recent collection events on OpenSea:</b>\n\n"
        link_text = "🔗 <b>Link:</b>"
        price_text = "💰 <b>Price:</b>"
        event_type_text = "🔄 <b>Event Type:</b>"
        chain_text = "🌐 <b>Chain:</b>"
        not_found_text = "❗️No recent collection events found on OpenSea."
        error_text = "❗️Error: Failed to fetch data from OpenSea API. Status: {}."
        client_error_text = "❗️There was an error fetching the data."
        unexpected_error_text = "❗️An unexpected error occurred."
        no_name_text = "🖼️ No Name"

    # Получаем параметры команды
    args = message.text.split()[1:]  # Получаем все аргументы после команды
    if not args:
        await message.reply("❗️Необходимо указать параметр collection_slug.")
        return

    # Формируем slug из первого параметра (collection_slug)
    collection_slug = args[0].lower().replace(' ', '-')

    # Разбираем дополнительные параметры (если есть)
    params = {
        "event_type": "sale",  # По умолчанию фильтруем только продажи
        "limit": "20",  # Устанавливаем максимальный лимит
    }

    for arg in args[1:]:  # Пропускаем первый аргумент (collection_slug)
        if '=' in arg:
            key, value = arg.split('=', 1)
            params[key.strip()] = value.strip()

    url = f"https://api.opensea.io/api/v2/events/collection/{collection_slug}"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                status_code = response.status
                if status_code == 200:
                    data = await response.json()
                    events = data.get('asset_events', [])

                    if events:
                        response_text = recent_events_text
                        for event in events:
                            nft_data = event.get('nft', {})
                            asset_name = nft_data.get('name', no_name_text)
                            asset_url = nft_data.get('opensea_url', '#')
                            payment_data = event.get('payment', {})
                            total_price = float(payment_data.get('quantity', 0)) / (10 ** payment_data.get('decimals', 18))
                            payment_token = payment_data.get('symbol', 'ETH')
                            chain = event.get('chain', 'ethereum').capitalize()
                            event_type = event.get('event_type', 'Sale').capitalize()

                            response_text += (
                                f"🔹 <b>{asset_name}</b>\n"
                                f"{link_text} <a href='{asset_url}'>OpenSea</a>\n"
                                f"{price_text} {total_price:.5f} {payment_token}\n"
                                f"{event_type_text} {event_type}\n"
                                f"{chain_text} {chain}\n\n"
                            )
                    else:
                        response_text = not_found_text

                else:
                    response_text = error_text.format(status_code)

        await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply(client_error_text)
        print(f"Ошибка запроса: {e}")

    except Exception as e:
        await message.reply(unexpected_error_text)
        print(f"Ошибка: {e}")


@dp.message(Command(commands=['nft_events_account']))
async def nft_events_account_handler(message: Message):
    # Получаем язык пользователя из базы данных
    user_language = get_user_language(message.from_user.id)

    # Устанавливаем язык сообщений на основе данных из базы
    if user_language == 'ru':
        recent_events_text = "🤖 <b>Последние события аккаунта на OpenSea:</b>\n\n"
        link_text = "🔗 <b>Ссылка:</b>"
        price_text = "💰 <b>Цена:</б>"
        event_type_text = "🔄 <b>Тип события:</б>"
        chain_text = "🌐 <b>Сеть:</б>"
        not_found_text = "❗️Не найдено недавних событий аккаунта на OpenSea."
        error_text = "❗️Ошибка: Не удалось получить данные от API OpenSea. Статус: {}."
        client_error_text = "❗️Произошла ошибка при получении данных."
        unexpected_error_text = "❗️Произошла непредвиденная ошибка."
        no_name_text = "🖼️ Без имени"
    else:
        recent_events_text = "🤖 <b>Recent account events on OpenSea:</b>\n\n"
        link_text = "🔗 <b>Link:</b>"
        price_text = "💰 <b>Price:</b>"
        event_type_text = "🔄 <b>Event Type:</b>"
        chain_text = "🌐 <b>Chain:</b>"
        not_found_text = "❗️No recent account events found on OpenSea."
        error_text = "❗️Error: Failed to fetch data from OpenSea API. Status: {}."
        client_error_text = "❗️There was an error fetching the data."
        unexpected_error_text = "❗️An unexpected error occurred."
        no_name_text = "🖼️ No Name"

    # Получаем параметры команды
    args = message.text.split()[1:]  # Получаем все аргументы после команды
    if not args:
        await message.reply("❗️Необходимо указать публичный адрес блокчейна.")
        return

    # Получаем адрес аккаунта из первого параметра
    account_address = args[0]

    # Разбираем дополнительные параметры (если есть)
    params = {
        "event_type": "sale",  # По умолчанию фильтруем только продажи
        "limit": "20",  # Устанавливаем максимальный лимит
    }

    for arg in args[1:]:  # Пропускаем первый аргумент (account_address)
        if '=' in arg:
            key, value = arg.split('=', 1)
            params[key.strip()] = value.strip()

    url = f"https://api.opensea.io/api/v2/events/accounts/{account_address}"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                status_code = response.status
                if status_code == 200:
                    data = await response.json()
                    events = data.get('asset_events', [])

                    if events:
                        response_text = recent_events_text
                        for event in events:
                            nft_data = event.get('nft', {})
                            asset_name = nft_data.get('name', no_name_text)
                            asset_url = nft_data.get('opensea_url', '#')
                            payment_data = event.get('payment', {})
                            total_price = float(payment_data.get('quantity', 0)) / (10 ** payment_data.get('decimals', 18))
                            payment_token = payment_data.get('symbol', 'ETH')
                            chain = event.get('chain', 'ethereum').capitalize()
                            event_type = event.get('event_type', 'Sale').capitalize()

                            response_text += (
                                f"🔹 <b>{asset_name}</b>\n"
                                f"{link_text} <a href='{asset_url}'>OpenSea</a>\n"
                                f"{price_text} {total_price:.5f} {payment_token}\n"
                                f"{event_type_text} {event_type}\n"
                                f"{chain_text} {chain}\n\n"
                            )
                    else:
                        response_text = not_found_text

                else:
                    response_text = error_text.format(status_code)

        await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply(client_error_text)
        print(f"Ошибка запроса: {e}")

    except Exception as e:
        await message.reply(unexpected_error_text)
        print(f"Ошибка: {e}")


@dp.message(Command(commands=['nft_get_account']))
async def nft_getaccount_handler(message: Message):
    # Получаем язык пользователя из базы данных
    user_language = get_user_language(message.from_user.id)

    # Устанавливаем язык сообщений на основе данных из базы
    if user_language == 'ru':
        account_profile_text = "🤖 <b>Профиль аккаунта на OpenSea:</b>\n\n"
        username_text = "🧑‍💻 <b>Имя пользователя:</b>"
        bio_text = "📄 <b>Биография:</b>"
        website_text = "🌐 <b>Сайт:</b>"
        joined_date_text = "📅 <b>Дата регистрации:</b>"
        social_media_text = "🔗 <b>Социальные сети:</b>"
        no_link_text = "нет ссылки"
    else:
        account_profile_text = "🤖 <b>Account profile on OpenSea:</b>\n\n"
        username_text = "🧑‍💻 <b>Username:</b>"
        bio_text = "📄 <b>Bio:</b>"
        website_text = "🌐 <b>Website:</b>"
        joined_date_text = "📅 <b>Joined Date:</b>"
        social_media_text = "🔗 <b>Social Media:</b>"
        no_link_text = "no link"

    # Получаем параметры команды
    args = message.text.split()[1:]  # Получаем все аргументы после команды
    if not args:
        await message.reply("❗️Необходимо указать публичный адрес блокчейна или имя пользователя.")
        return

    # Получаем адрес или имя пользователя
    account_identifier = args[0]

    url = f"https://api.opensea.io/api/v2/accounts/{account_identifier}"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                status_code = response.status
                if status_code == 200:
                    data = await response.json()

                    # Сборка ответа
                    response_text = account_profile_text
                    response_text += f"{username_text} {data.get('username', 'No Username')}\n"
                    response_text += f"{bio_text} {data.get('bio', 'No Bio')}\n"

                    # Проверка наличия ссылки на сайт
                    website = data.get('website', None)
                    if website:
                        response_text += f"{website_text} <a href='{website}'>{website}</a>\n"
                    else:
                        response_text += f"{website_text} {no_link_text}\n"

                    response_text += f"{joined_date_text} {data.get('joined_date', 'No Date')}\n"

                    if 'social_media_accounts' in data:
                        social_media_accounts = data['social_media_accounts']
                        if social_media_accounts:
                            response_text += f"{social_media_text}\n"
                            for account in social_media_accounts:
                                response_text += f"{account['platform']}: {account['username']}\n"

                    # Если нет ссылки на сайт, добавляем изображение в конец сообщения
                    profile_image_url = data.get('profile_image_url', None)
                    if not website and profile_image_url:
                        await message.reply_photo(photo=profile_image_url, caption=response_text, parse_mode="HTML")
                        return

                else:
                    response_text = f"❗️Ошибка: Не удалось получить данные от API OpenSea. Статус: {status_code}."

        await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply("❗️Произошла ошибка при получении данных.")
        print(f"Ошибка запроса: {e}")

    except Exception as e:
        await message.reply("❗️Произошла непредвиденная ошибка.")
        print(f"Ошибка: {e}")

@dp.message(Command(commands=['nft_get_contract']))
async def nft_get_contract_handler(message: Message):
    # Получаем язык пользователя из базы данных
    user_language = get_user_language(message.from_user.id)

    # Устанавливаем язык сообщений на основе данных из базы
    if user_language == 'ru':
        contract_info_text = "🤖 <b>Информация о смарт-контракте на OpenSea:</b>\n\n"
        address_text = "🏦 <b>Адрес:</b>"
        chain_text = "⛓️ <b>Цепочка:</b>"
        collection_text = "🖼️ <b>Коллекция:</b>"
        contract_standard_text = "📜 <b>Стандарт контракта:</b>"
        name_text = "📛 <b>Имя контракта:</b>"
        total_supply_text = "🔢 <b>Общее количество:</b>"
        error_text = "❗️Ошибка: Не удалось получить данные от API OpenSea. Статус: {}."
        not_found_text = "❗️Смарт-контракт не найден для указанного адреса на цепочке {}."
        client_error_text = "❗️Произошла ошибка при получении данных."
        unexpected_error_text = "❗️Произошла непредвиденная ошибка."
    else:
        contract_info_text = "🤖 <b>Contract Information on OpenSea:</b>\n\n"
        address_text = "🏦 <b>Address:</b>"
        chain_text = "⛓️ <b>Chain:</b>"
        collection_text = "🖼️ <b>Collection:</b>"
        contract_standard_text = "📜 <b>Contract Standard:</b>"
        name_text = "📛 <b>Contract Name:</b>"
        total_supply_text = "🔢 <b>Total Supply:</b>"
        error_text = "❗️Error: Failed to fetch data from OpenSea API. Status: {}."
        not_found_text = "❗️Smart contract not found for the provided address on the {} chain."
        client_error_text = "❗️There was an error fetching the data."
        unexpected_error_text = "❗️An unexpected error occurred."

    # Получаем параметры команды
    args = message.text.split()[1:]  # Получаем все аргументы после команды
    if len(args) < 2:
        await message.reply("❗️Необходимо указать цепочку и публичный адрес блокчейна.")
        return

    # Получаем цепочку и адрес
    chain = args[0].lower()
    address = args[1]

    # Формируем URL без проверки входных данных
    url = f"https://api.opensea.io/api/v2/chain/{chain}/contract/{address}"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                status_code = response.status

                if status_code == 200:
                    data = await response.json()

                    # Проверяем, существует ли контракт
                    if 'address' in data and data['address']:
                        # Сборка ответа
                        response_text = contract_info_text
                        response_text += f"{address_text} {data.get('address', 'No Address')}\n"
                        response_text += f"{chain_text} {data.get('chain', 'No Chain')}\n"
                        response_text += f"{collection_text} {data.get('collection', 'No Collection')}\n"
                        response_text += f"{contract_standard_text} {data.get('contract_standard', 'No Standard')}\n"
                        response_text += f"{name_text} {data.get('name', 'No Name')}\n"
                        response_text += f"{total_supply_text} {data.get('total_supply', 'No Supply')}\n"
                    else:
                        # Если контракт не найден, отправляем сообщение
                        response_text = not_found_text.format(chain)
                else:
                    response_text = error_text.format(status_code)

        await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply(client_error_text)

    except Exception as e:
        await message.reply(unexpected_error_text)


# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dp.message(Command(commands=['nft_get_nft']))
async def nft_get_nft_handler(message: Message):
    # Получаем язык пользователя из базы данных
    user_language = get_user_language(message.from_user.id)

    # Устанавливаем язык сообщений на основе данных из базы
    if user_language == 'ru':
        nft_info_text = "🤖 <b>Информация о NFT:</b>\n\n"
        identifier_text = "🆔 <b>Идентификатор:</b>"
        collection_text = "🖼️ <b>Коллекция:</b>"
        contract_text = "🏦 <b>Контракт:</b>"
        name_text = "📛 <b>Имя:</b>"
        description_text = "📝 <b>Описание:</b>"
        image_url_text = "🖼️ <b>Изображение:</b>"
        metadata_url_text = "🔗 <b>URL метаданных:</b>"
        opensea_url_text = "🌐 <b>OpenSea URL:</b>"
        rarity_text = "⭐️ <b>Редкость:</b>"
        owners_text = "👥 <b>Владельцы:</b>"
        traits_text = "🔍 <b>Характеристики:</б>"
        error_text = "❗️Ошибка: Не удалось получить данные от API OpenSea. Статус: {}."
        not_found_text = "❗️NFT не найден для указанного идентификатора на цепочке {}."
        client_error_text = "❗️Произошла ошибка при получении данных."
        unexpected_error_text = "❗️Произошла непредвиденная ошибка."
    else:
        nft_info_text = "🤖 <b>NFT Information:</b>\n\n"
        identifier_text = "🆔 <b>Identifier:</b>"
        collection_text = "🖼️ <b>Collection:</b>"
        contract_text = "🏦 <b>Contract:</b>"
        name_text = "📛 <b>Name:</b>"
        description_text = "📝 <b>Description:</b>"
        image_url_text = "🖼️ <b>Image URL:</b>"
        metadata_url_text = "🔗 <b>Metadata URL:</b>"
        opensea_url_text = "🌐 <b>OpenSea URL:</b>"
        rarity_text = "⭐️ <b>Rarity:</b>"
        owners_text = "👥 <b>Owners:</b>"
        traits_text = "🔍 <b>Traits:</b>"
        error_text = "❗️Error: Failed to fetch data from OpenSea API. Status: {}."
        not_found_text = "❗️NFT not found for the provided identifier on the {} chain."
        client_error_text = "❗️There was an error fetching the data."
        unexpected_error_text = "❗️An unexpected error occurred."

    # Получаем параметры команды
    args = message.text.split()[1:]  # Получаем все аргументы после команды
    if len(args) < 3:
        await message.reply("❗️Необходимо указать цепочку, адрес контракта и идентификатор NFT.")
        return

    # Получаем цепочку, адрес контракта и идентификатор NFT
    chain = args[0].lower()
    address = args[1]
    identifier = args[2]

    # Формируем URL для запроса
    url = f"https://api.opensea.io/api/v2/chain/{chain}/contract/{address}/nfts/{identifier}"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                status_code = response.status
                logger.info(f"Response status code: {status_code}")  # Логируем статус ответа

                if status_code == 200:
                    data = await response.json()
                    logger.info(f"Received data: {data}")  # Логируем полученные данные

                    if not data:
                        logger.error("Received empty response from API")
                        await message.reply(not_found_text.format(chain))
                        return

                    nft = data.get('nft')
                    logger.info(f"NFT data extracted: {nft}")  # Логируем данные о NFT

                    if nft is None:
                        logger.error(f"'nft' key is missing or None in response: {data}")
                        await message.reply(not_found_text.format(chain))
                        return

                    # Обработка данных о редкости (rarity)
                    rarity = nft.get('rarity', {})
                    rank = rarity.get('rank', 'No Rank') if rarity else 'No Rank'
                    score = rarity.get('score', 'No Score') if rarity else 'No Score'

                    # Сборка ответа
                    response_text = nft_info_text
                    response_text += f"{identifier_text} {nft.get('identifier', 'No Identifier')}\n"
                    response_text += f"{collection_text} {nft.get('collection', 'No Collection')}\n"
                    response_text += f"{contract_text} {nft.get('contract', 'No Contract')}\n"
                    response_text += f"{name_text} {nft.get('name', 'No Name')}\n"
                    response_text += f"{description_text} {nft.get('description', 'No Description')}\n"
                    response_text += f"{image_url_text} {nft.get('image_url', 'No Image')}\n"
                    response_text += f"{metadata_url_text} {nft.get('metadata_url', 'No Metadata URL')}\n"
                    response_text += f"{opensea_url_text} {nft.get('opensea_url', 'No OpenSea URL')}\n"
                    response_text += f"{rarity_text} Rank: {rank} Score: {score}\n"

                    # Владельцы
                    owners_info = "\n".join(
                        [f"  - {owner.get('address', 'No Address')} (Quantity: {owner.get('quantity', 'No Quantity')})"
                         for owner in nft.get('owners', [])])
                    response_text += f"{owners_text}\n{owners_info}\n"

                    # Характеристики
                    traits_info = "\n".join(
                        [f"  - {trait.get('trait_type', 'No Type')}: {trait.get('value', 'No Value')}" for trait in
                         nft.get('traits', [])])
                    response_text += f"{traits_text}\n{traits_info}\n"

                else:
                    response_text = error_text.format(status_code)

        await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply(client_error_text)
        logger.error(f"ClientError: {e}")  # Логируем исключение aiohttp

    except Exception as e:
        await message.reply(unexpected_error_text)
        logger.error(f"Exception: {e}")  # Логируем любое другое исключение


# Настраиваем логирование для ошибок
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@dp.message(Command(commands=['nft_listings_collection']))
async def nft_listings_collection_handler(message: Message):
    # Получаем язык пользователя из базы данных
    user_language = get_user_language(message.from_user.id)

    # Языковая адаптация
    if user_language == 'ru':
        listings_info_text = "🤖 <b>Активные листинги коллекции:</b>\n\n"
        error_text = "❗️Ошибка: Не удалось получить данные от API OpenSea. Статус: {}."
        client_error_text = "❗️Произошла ошибка при получении данных."
        unexpected_error_text = "❗️Произошла непредвиденная ошибка."
        no_listings_text = "❗️В коллекции не найдено активных листингов."
        listing_text = "📜 <b>Листинг:</b>\n"
        price_text = "💰 <b>Цена:</b>"
        seller_text = "👤 <b>Продавец:</b>"
        start_time_text = "🕒 <b>Начало:</b>"
        end_time_text = "⌛️ <b>Окончание:</b>"
        link_text = "🔗 <b>Ссылка на объект:</b>"
    else:
        listings_info_text = "🤖 <b>Active Collection Listings:</b>\n\n"
        error_text = "❗️Error: Failed to fetch data from OpenSea API. Status: {}."
        client_error_text = "❗️There was an error fetching the data."
        unexpected_error_text = "❗️An unexpected error occurred."
        no_listings_text = "❗️No active listings found in the collection."
        listing_text = "📜 <b>Listing:</b>\n"
        price_text = "💰 <b>Price:</b>"
        seller_text = "👤 <b>Seller:</b>"
        start_time_text = "🕒 <b>Start Time:</b>"
        end_time_text = "⌛️ <b>End Time:</b>"
        link_text = "🔗 <b>Link to Item:</b>"

    # Получаем параметры команды
    args = message.text.split()[1:]  # Получаем все аргументы после команды
    if len(args) < 1:
        await message.reply(error_text.format("Missing collection slug"))
        return

    # Получаем slug коллекции и лимит
    collection_slug = args[0]
    limit = int(args[1]) if len(args) > 1 else 15

    # Формируем URL для запроса
    url = f"https://api.opensea.io/api/v2/listings/collection/{collection_slug}/all?limit={limit}"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                status_code = response.status

                if status_code == 200:
                    data = await response.json()

                    if not data or 'listings' not in data or len(data['listings']) == 0:
                        await message.reply(no_listings_text)
                        return

                    listings = data['listings']
                    response_text = listings_info_text

                    for listing in listings:
                        price_info = listing.get('price', {}).get('current', {})
                        protocol_data = listing.get('protocol_data', {}).get('parameters', {})
                        offer = protocol_data.get('offer', [])[0] if protocol_data.get('offer') else {}
                        offerer = protocol_data.get('offerer', 'Unknown')
                        currency = price_info.get('currency', 'Unknown')
                        value_in_wei = int(price_info.get('value', '0'))
                        value_in_eth = value_in_wei / 10**18  # Преобразование из Wei в ETH

                        # Преобразование времени из Unix в обычный формат
                        start_time = int(protocol_data.get('startTime', '0'))
                        end_time = int(protocol_data.get('endTime', '0'))
                        start_time_formatted = datetime.fromtimestamp(start_time).strftime('%d/%m/%Y %H:%M:%S')
                        end_time_formatted = datetime.fromtimestamp(end_time).strftime('%d/%m/%Y %H:%M:%S')

                        # Формируем ссылку на объект
                        contract_address = offer.get('token', 'Unknown')
                        token_id = offer.get('identifierOrCriteria', 'Unknown')
                        link = f"https://opensea.io/assets/ethereum/{contract_address}/{token_id}"

                        response_text += (
                            f"{listing_text}\n"
                            f"{price_text} {value_in_eth:.6f} {currency}\n"  # Отображаем цену в ETH
                            f"{seller_text} {offerer}\n"
                            f"{start_time_text} {start_time_formatted}\n"  # Преобразованное время начала
                            f"{end_time_text} {end_time_formatted}\n"  # Преобразованное время окончания
                            f"{link_text} <a href='{link}'>OpenSea</a>\n"
                            f"---\n"
                        )

                    await message.reply(response_text, parse_mode="HTML")

                else:
                    response_text = error_text.format(status_code)
                    await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply(client_error_text)
        logger.error(f"ClientError: {e}")  # Логируем исключение aiohttp

    except Exception as e:
        await message.reply(unexpected_error_text)
        logger.error(f"Exception: {e}")  # Логируем любое другое исключение



# Настраиваем логирование для ошибок
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@dp.message(Command(commands=['nft_offers_collection']))
async def nft_offers_collection_handler(message: Message):
    # Получаем язык пользователя из базы данных
    user_language = get_user_language(message.from_user.id)

    # Языковая адаптация
    if user_language == 'ru':
        offers_info_text = "🤖 <b>Активные предложения коллекции:</b>\n\n"
        error_text = "❗️Ошибка: Не удалось получить данные от API OpenSea. Статус: {}."
        client_error_text = "❗️Произошла ошибка при получении данных."
        unexpected_error_text = "❗️Произошла непредвиденная ошибка."
        no_offers_text = "❗️В коллекции не найдено активных предложений."
        offer_text = "📜 <b>Предложение:</b>\n"
        price_text = "💰 <b>Цена:</b>"
        offerer_text = "👤 <b>Предложил:</b>"
        criteria_text = "📑 <b>Критерии:</b>"
        start_time_text = "🕒 <b>Начало:</b>"
        end_time_text = "⌛️ <b>Окончание:</b>"
        link_text = "🔗 <b>Ссылка на объект:</b>"
    else:
        offers_info_text = "🤖 <b>Active Collection Offers:</b>\n\n"
        error_text = "❗️Error: Failed to fetch data from OpenSea API. Status: {}."
        client_error_text = "❗️There was an error fetching the data."
        unexpected_error_text = "❗️An unexpected error occurred."
        no_offers_text = "❗️No active offers found in the collection."
        offer_text = "📜 <b>Offer:</b>\n"
        price_text = "💰 <b>Price:</b>"
        offerer_text = "👤 <b>Offerer:</b>"
        criteria_text = "📑 <b>Criteria:</b>"
        start_time_text = "🕒 <b>Start Time:</b>"
        end_time_text = "⌛️ <b>End Time:</b>"
        link_text = "🔗 <b>Link to Item:</b>"

    # Получаем параметры команды
    args = message.text.split()[1:]  # Получаем все аргументы после команды
    if len(args) < 1:
        await message.reply(error_text.format("Missing collection slug"))
        return

    # Получаем slug коллекции и лимит
    collection_slug = args[0]
    limit = int(args[1]) if len(args) > 1 else 15

    # Формируем URL для запроса
    url = f"https://api.opensea.io/api/v2/offers/collection/{collection_slug}/all?limit={limit}"
    headers = {
        "X-API-KEY": settings.opensea_api_key
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                status_code = response.status

                if status_code == 200:
                    data = await response.json()
                    logger.error(f"Received data: {data}")  # Логируем полный ответ от API

                    if not data or 'offers' not in data or len(data['offers']) == 0:
                        await message.reply(no_offers_text)
                        return

                    offers = data.get('offers', [])
                    response_text = offers_info_text

                    for offer in offers:
                        price_info = offer.get('price', {})
                        protocol_data = offer.get('protocol_data', {}).get('parameters', {})
                        criteria = offer.get('criteria', {})
                        offerer = protocol_data.get('offerer', 'Unknown') if protocol_data else 'Unknown'
                        currency = price_info.get('currency', 'Unknown') if price_info else 'Unknown'
                        value_in_wei = int(price_info.get('value', '0')) if price_info else 0
                        value_in_eth = value_in_wei / 10**18  # Преобразование из Wei в ETH

                        # Преобразование времени из Unix в обычный формат
                        start_time = int(protocol_data.get('startTime', '0')) if protocol_data else 0
                        end_time = int(protocol_data.get('endTime', '0')) if protocol_data else 0
                        start_time_formatted = datetime.fromtimestamp(start_time).strftime('%d/%m/%Y %H:%M:%S') if start_time else 'Unknown'
                        end_time_formatted = datetime.fromtimestamp(end_time).strftime('%d/%m/%Y %H:%M:%S') if end_time else 'Unknown'

                        # Выводим больше данных о критериях
                        contract_address = criteria.get('contract', {}).get('address', 'Unknown') if criteria else 'Unknown'
                        token_id = criteria.get('encoded_token_ids', 'Unknown') if criteria else 'Unknown'
                        trait_type = criteria.get('trait', {}).get('type', 'N/A')
                        trait_value = criteria.get('trait', {}).get('value', 'N/A')
                        link = f"https://opensea.io/assets/ethereum/{contract_address}/{token_id}" if contract_address != 'Unknown' and token_id != 'Unknown' else "N/A"

                        response_text += (
                            f"{offer_text}\n"
                            f"{price_text} {value_in_eth:.6f} {currency}\n"  # Отображаем цену в ETH
                            f"{offerer_text} {offerer}\n"
                            f"{criteria_text} Contract: {contract_address}, Token ID: {token_id}, Trait: {trait_type} - {trait_value}\n"
                            f"{start_time_text} {start_time_formatted}\n"  # Преобразованное время начала
                            f"{end_time_text} {end_time_formatted}\n"  # Преобразованное время окончания
                            f"{link_text} <a href='{link}'>OpenSea</a>\n" if link != "N/A" else f"{link_text} N/A\n"
                            f"---\n"
                        )

                    await message.reply(response_text, parse_mode="HTML")

                else:
                    response_text = error_text.format(status_code)
                    await message.reply(response_text, parse_mode="HTML")

    except aiohttp.ClientError as e:
        await message.reply(client_error_text)
        logger.error(f"ClientError: {e}")  # Логируем исключение aiohttp

    except Exception as e:
        await message.reply(unexpected_error_text)
        logger.error(f"Exception: {e}")  # Логируем любое другое исключение

