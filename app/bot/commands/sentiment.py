import aiohttp  # Для выполнения асинхронных HTTP-запросов
import os  # Для работы с файловой системой (удаление файлов)
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message, FSInputFile  # Для работы с сообщениями Telegram и отправки файлов
from bot import dp  # Для доступа к диспетчеру вашего бота


# Функция для получения значения индекса страха и жадности
async def fetch_sentiment_data():
    url = "https://api.alternative.me/fng/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['data'][0]
            else:
                raise Exception(f"Ошибка загрузки данных: {response.status}")

# Функция для получения изображения индекса настроения
async def fetch_sentiment_image():
    url = "https://alternative.me/crypto/fear-and-greed-index.png"
    image_path = "sentiment.png"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(image_path, 'wb') as f:
                    f.write(await response.read())
                return image_path
            else:
                raise Exception(f"Ошибка загрузки изображения: {response.status}")

# Обработчик команды /sentiment 
@dp.message(Command(commands=['sentiment']))
async def send_sentiment(message: Message):
    global caption
    try:
        # Получаем значение индекса и изображение
        sentiment_data = await fetch_sentiment_data()
        image_path = await fetch_sentiment_image()

        # Определяем статус по значению индекса
        value = int(sentiment_data['value'])
        status = sentiment_data['value_classification']

        # Формируем подпись в зависимости от языка команды
        if message.text.startswith("/sentiment"):
            caption = f"Crypto Sentiment of Today 🙏\n" \
                      f"💡 Status: {status}\n" \
                      f"📊 Value: {value}/100"
        elif message.text.startswith("/настроение"):
            caption = f"Настроение криптовалютного рынка на сегодня 🙏\n" \
                      f"💡 Статус: {status}\n" \
                      f"📊 Значение: {value}/100"

        # Отправляем изображение пользователю
        await message.answer_photo(FSInputFile(image_path), caption=caption)

        # Опционально: удаление файла после отправки
        os.remove(image_path)

    except Exception as e:
        await message.reply("Произошла ошибка при получении индекса настроения.")
        print(f"Ошибка: {e}")