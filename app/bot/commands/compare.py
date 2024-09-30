import aiohttp  # Для выполнения асинхронных HTTP-запросов
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message  # Для обработки сообщений Telegram
from bot import dp  # Для доступа к диспетчеру вашего бота
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя

@dp.message(Command(commands=['compare']))
async def compare_cryptos(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        language = get_user_language(message.from_user.id)  # Предполагается, что функция синхронная
        is_russian = (language == 'ru')

        # Извлекаем символы криптовалют из команды
        args = message.text.split()
        if len(args) < 3:
            if is_russian:
                await message.reply("❗️ Пожалуйста, используйте команду в формате: /compare [symbol1] [symbol2] ...")
            else:
                await message.reply("❗️ Please use the command in the format: /compare [symbol1] [symbol2] ...")
            return

        crypto_symbols = [symbol.upper() for symbol in args[1:]]  # Преобразуем символы в верхний регистр
        symbols_query = ",".join(crypto_symbols)
        url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbols_query}&tsyms=USD,ETH"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    if is_russian:
                        await message.reply("❌ Не удалось получить данные для указанных криптовалют.")
                    else:
                        await message.reply("❌ Failed to retrieve data for the specified cryptocurrencies.")
                    return

                data = await response.json()

                if 'RAW' not in data:
                    if is_russian:
                        await message.reply("❌ Не удалось получить данные для указанных криптовалют.")
                    else:
                        await message.reply("❌ Failed to retrieve data for the specified cryptocurrencies.")
                    return

                # Формируем сообщение с данными для сравнения
                comparison_message = "📊 **Сравнение криптовалют**:\n" if is_russian else "📊 **Cryptocurrency Comparison**:\n"

                for symbol in crypto_symbols:
                    if symbol in data['RAW']:
                        raw_data_usd = data['RAW'][symbol]['USD']
                        raw_data_eth = data['RAW'][symbol].get('ETH', {})
                        
                        price = raw_data_usd.get('PRICE', 'N/A')
                        market_cap = raw_data_usd.get('MKTCAP', 'N/A')
                        volume_24h = raw_data_usd.get('VOLUME24HOUR', 'N/A')
                        high_24h = raw_data_usd.get('HIGH24HOUR', 'N/A')
                        low_24h = raw_data_usd.get('LOW24HOUR', 'N/A')
                        change_1h = raw_data_usd.get('CHANGEHOUR', 'N/A')
                        change_pct_24h = raw_data_usd.get('CHANGEPCT24HOUR', 'N/A')
                        price_eth = raw_data_eth.get('PRICE', 'N/A')

                        # Обработка значений, которые могут быть 'N/A'
                        def format_value(value, decimals=2):
                            if isinstance(value, (int, float)):
                                return f"${value:,.{decimals}f}"
                            return value

                        price_formatted = format_value(price)
                        market_cap_formatted = format_value(market_cap)
                        volume_24h_formatted = format_value(volume_24h)
                        high_24h_formatted = format_value(high_24h)
                        low_24h_formatted = format_value(low_24h)
                        change_1h_formatted = format_value(change_1h)
                        change_pct_24h_formatted = f"{change_pct_24h}%" if change_pct_24h != 'N/A' else 'N/A'
                        price_eth_formatted = f"{price_eth:.6f}" if isinstance(price_eth, (int, float)) else price_eth

                        if is_russian:
                            comparison_message += (
                                f"\n🔹 **{symbol}**\n"
                                f"   💰 **Цена**: {price_formatted}\n"
                                f"   📊 **Рыночная капитализация**: {market_cap_formatted}\n"
                                f"   🔄 **Объем торгов (24ч)**: {volume_24h_formatted}\n"
                                f"   📈 **Макс/Мин за 24ч**: {high_24h_formatted} / {low_24h_formatted}\n"
                                f"   ⏳ **Изменение за 1ч**: {change_1h_formatted}\n"
                                f"   📉 **Изменение за 24ч**: {change_pct_24h_formatted}\n"
                                f"   🪙 **1 {symbol} = {price_eth_formatted} ETH**\n"
                            )
                        else:
                            comparison_message += (
                                f"\n🔹 **{symbol}**\n"
                                f"   💰 **Price**: {price_formatted}\n"
                                f"   📊 **Market Cap**: {market_cap_formatted}\n"
                                f"   🔄 **24h Trading Volume**: {volume_24h_formatted}\n"
                                f"   📈 **24h High/Low**: {high_24h_formatted} / {low_24h_formatted}\n"
                                f"   ⏳ **1h Change**: {change_1h_formatted}\n"
                                f"   📉 **24h Change**: {change_pct_24h_formatted}\n"
                                f"   🪙 **1 {symbol} = {price_eth_formatted} ETH**\n"
                            )
                    else:
                        if is_russian:
                            comparison_message += f"\n🔹 **{symbol}**: Данные не найдены\n"
                        else:
                            comparison_message += f"\n🔹 **{symbol}**: Data not available\n"

                await message.reply(comparison_message, parse_mode="Markdown")

    except Exception as e:
        # В случае ошибки отправляем сообщение на нужном языке
        if 'is_russian' in locals() and is_russian:
            await message.reply("⚠️ Произошла ошибка при получении данных. Пожалуйста, попробуйте позже.")
        else:
            await message.reply("⚠️ An error occurred while fetching the data. Please try again later.")
        print(f"Ошибка: {e}")
