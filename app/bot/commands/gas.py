import aiohttp  # Для выполнения асинхронных HTTP-запросов
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message  # Для обработки сообщений Telegram
from bot import dp  # Для доступа к диспетчеру вашего бота
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя
from config import settings


@dp.message(Command(commands=['gas']))
async def get_gas_fees(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        user_id = message.from_user.id
        language = get_user_language(user_id)

        # Определяем язык и устанавливаем флаг
        is_russian = language == 'ru'

        # Используем API-ключ от Etherscan для получения данных о газовых сборах
        eth_url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={settings.etherscan_api_key}"

        async with aiohttp.ClientSession() as session:
            async with session.get(eth_url) as response:
                if response.status == 200:
                    eth_data = await response.json()
                    if eth_data.get('status') == "1":
                        gas_data = eth_data['result']

                        gas_message = (
                            "⛽️ **Ethereum Gas Fees**:\n" if not is_russian else "⛽️ **Газовые сборы Ethereum**:\n"
                        )
                        gas_message += (
                            f"🔹 **Low**: {gas_data.get('SafeGasPrice', 'N/A')} Gwei\n" if not is_russian
                            else f"🔹 **Низкие**: {gas_data.get('SafeGasPrice', 'N/A')} Gwei\n"
                        )
                        gas_message += (
                            f"🔸 **Average**: {gas_data.get('ProposeGasPrice', 'N/A')} Gwei\n" if not is_russian
                            else f"🔸 **Средние**: {gas_data.get('ProposeGasPrice', 'N/A')} Gwei\n"
                        )
                        gas_message += (
                            f"🔺 **High**: {gas_data.get('FastGasPrice', 'N/A')} Gwei\n" if not is_russian
                            else f"🔺 **Высокие**: {gas_data.get('FastGasPrice', 'N/A')} Gwei\n"
                        )

                        # Проверяем наличие дополнительных данных в ответе API
                        if 'suggestBaseFee' in gas_data:
                            gas_message += (
                                f"\n⏳ **Estimated Base Fee**: {gas_data['suggestBaseFee']} Gwei\n" if not is_russian
                                else f"\n⏳ **Оценочная базовая комиссия**: {gas_data['suggestBaseFee']} Gwei\n"
                            )
                        if 'blockTime' in gas_data:
                            gas_message += (
                                f"⛏ **Block Time**: {gas_data['blockTime']} seconds\n" if not is_russian
                                else f"⛏ **Время блока**: {gas_data['blockTime']} секунд\n"
                            )
                        if 'lastBlock' in gas_data:
                            gas_message += (
                                f"📊 **Last Block**: {gas_data['lastBlock']}\n" if not is_russian
                                else f"📊 **Последний блок**: {gas_data['lastBlock']}\n"
                            )
                    else:
                        gas_message = (
                            "❌ Failed to retrieve data from Etherscan." if not is_russian
                            else "❌ Не удалось получить данные от Etherscan."
                        )
                else:
                    gas_message = (
                        "❌ Error: Unable to fetch data." if not is_russian
                        else "❌ Ошибка: Не удалось получить данные."
                    )

        # Отправляем сообщение пользователю
        await message.reply(gas_message, parse_mode="Markdown")

    except Exception as e:
        # В случае ошибки отправляем сообщение на нужном языке
        error_message = (
            "⚠️ An error occurred while fetching gas fees data. Please try again later." if not is_russian
            else "⚠️ Произошла ошибка при получении данных о газовых сборах. Пожалуйста, попробуйте позже."
        )
        await message.reply(error_message)
        print(f"Ошибка: {e}")
