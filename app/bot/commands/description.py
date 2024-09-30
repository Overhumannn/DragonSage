import aiohttp  # Для выполнения асинхронных HTTP-запросов
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message  # Для обработки сообщений Telegram
from bot import dp  # Для доступа к диспетчеру вашего бота
from deep_translator import GoogleTranslator  # Для перевода текста

from app.database.crud import get_user_language  # Импортируем функцию для получения языка пользователя

@dp.message(Command(commands=['description']))
async def get_crypto_description(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        language = get_user_language(message.from_user.id)  # Убрали 'await'
        if language not in ['en', 'ru']:
            language = 'en'  # Устанавливаем английский по умолчанию, если язык не задан или неизвестен

        # Инициализация переводчика, если нужен перевод на русский
        translator = None
        if language == 'ru':
            translator = GoogleTranslator(source='en', target='ru')

        # Сообщения для разных языков
        messages = {
            'en': {
                'usage': "❗️ Please use the command in the format: /description [symbol]",
                'api_error': "❌ Failed to retrieve data for the specified cryptocurrency.",
                'not_found': "❌ Data for the specified cryptocurrency not found.",
                'error': "⚠️ An error occurred while fetching the data. Please try again later.",
                'fields': (
                    "🪙 **{full_name} - ${symbol}**\n\n"
                    "💵 **Current Price**: ${current_price:,.2f}\n"
                    "📊 **Market Cap**: ${market_cap:,.2f}\n"
                    "🔄 **24h Trading Volume**: ${volume_24h:,.2f}\n\n"
                    "ℹ️ **Description**: {description}\n\n"
                    "🌐 **Website**: {website}\n"
                )
            },
            'ru': {
                'usage': "❗️ Пожалуйста, используйте команду в формате: /description [symbol]",
                'api_error': "❌ Не удалось получить данные для указанной криптовалюты.",
                'not_found': "❌ Данные по указанной криптовалюте не найдены.",
                'error': "⚠️ Произошла ошибка при получении данных. Пожалуйста, попробуйте позже.",
                'fields': (
                    "🪙 **{full_name} - ${symbol}**\n\n"
                    "💵 **Текущая цена**: ${current_price:,.2f}\n"
                    "📊 **Рыночная капитализация**: ${market_cap:,.2f}\n"
                    "🔄 **Объем торгов (24ч)**: ${volume_24h:,.2f}\n\n"
                    "ℹ️ **Описание**: {description}\n\n"
                    "🌐 **Веб-сайт**: {website}\n"
                )
            }
        }

        lang = messages.get(language, messages['en'])  # По умолчанию 'en'

        # Извлекаем символ криптовалюты из команды
        args = message.text.split()
        if len(args) != 2:
            await message.reply(lang['usage'])
            return

        crypto_symbol = args[1].upper()

        # Запрос данных с CryptoCompare API для получения общей информации
        url = "https://min-api.cryptocompare.com/data/all/coinlist"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await message.reply(lang['api_error'])
                    return

                data = await response.json()

                if 'Data' not in data or crypto_symbol not in data['Data']:
                    await message.reply(lang['not_found'])
                    return

                crypto_data = data['Data'][crypto_symbol]

                # Формирование описания
                name = crypto_data.get('CoinName', crypto_symbol)
                full_name = crypto_data.get('FullName', name)
                description = crypto_data.get('Description', 'No description available.')
                website = crypto_data.get('AssetWebsiteUrl', 'N/A')

                # Перевод описания на русский язык, если выбран русский язык и описание доступно
                if language == 'ru' and description != 'No description available.':
                    try:
                        description = translator.translate(description)
                    except Exception as e:
                        # В случае ошибки перевода, оставляем оригинальное описание
                        print(f"Ошибка перевода: {e}")

        # Запрос текущей цены, объема торгов и рыночной капитализации
        price_url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={crypto_symbol}&tsyms=USD"
        async with aiohttp.ClientSession() as session:
            async with session.get(price_url) as response:
                if response.status != 200:
                    # Если не удалось получить цену, устанавливаем значения как 'N/A'
                    current_price = 'N/A'
                    market_cap = 'N/A'
                    volume_24h = 'N/A'
                else:
                    price_data = await response.json()

                    if not price_data or 'RAW' not in price_data or crypto_symbol not in price_data['RAW']:
                        current_price = 'N/A'
                        market_cap = 'N/A'
                        volume_24h = 'N/A'
                    else:
                        price_info = price_data['RAW'][crypto_symbol]['USD']
                        current_price = price_info.get('PRICE', 'N/A')
                        market_cap = price_info.get('MKTCAP', 'N/A')
                        volume_24h = price_info.get('VOLUME24HOUR', 'N/A')

        # Формирование ответа
        try:
            if language == 'ru':
                response_message = lang['fields'].format(
                    full_name=full_name,
                    symbol=crypto_symbol,
                    current_price=float(current_price) if current_price != 'N/A' else current_price,
                    market_cap=float(market_cap) if market_cap != 'N/A' else market_cap,
                    volume_24h=float(volume_24h) if volume_24h != 'N/A' else volume_24h,
                    description=description,
                    website=website
                )
            else:
                response_message = lang['fields'].format(
                    full_name=full_name,
                    symbol=crypto_symbol,
                    current_price=float(current_price) if current_price != 'N/A' else current_price,
                    market_cap=float(market_cap) if market_cap != 'N/A' else market_cap,
                    volume_24h=float(volume_24h) if volume_24h != 'N/A' else volume_24h,
                    description=description,
                    website=website
                )
        except Exception as e:
            await message.reply(lang['error'])
            print(f"Ошибка при формировании сообщения: {e}")
            return

        await message.reply(response_message, parse_mode="Markdown")

    except Exception as e:
        # В случае непредвиденной ошибки, отправляем сообщение об ошибке
        error_messages = {
            'en': "⚠️ An error occurred while fetching the data. Please try again later.",
            'ru': "⚠️ Произошла ошибка при получении данных. Пожалуйста, попробуйте позже."
        }
        # Пытаемся определить язык, если он уже был получен
        language = language if 'language' in locals() else 'en'
        await message.reply(error_messages.get(language, error_messages['en']))
        print(f"Ошибка: {e}")
