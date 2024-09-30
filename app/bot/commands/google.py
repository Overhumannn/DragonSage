import os  # Для работы с файловой системой (удаление файлов)
import matplotlib.pyplot as plt  # Для построения графиков
import matplotlib.dates as mdates  # Для форматирования дат на оси X
from pytrends.request import TrendReq  # Для работы с Google Trends API через pytrends
import aiohttp  # Для выполнения асинхронных HTTP-запросов
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message, FSInputFile  # Для обработки сообщений Telegram и отправки файлов
from bot import dp  # Для доступа к диспетчеру вашего бота
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя


# Функция для инициализации pytrends с параметром языка
def initialize_pytrends(language='en-US'):
    return TrendReq(hl=language, tz=360)


# Функция для получения данных Google Trends и построения графика
def get_google_trends(keyword, language='en-US'):
    pytrends = initialize_pytrends(language=language)
    pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')

    data = pytrends.interest_over_time()

    if data.empty:
        return None

    # Построение графика
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data[keyword], label=keyword, color='blue', linewidth=2)
    plt.title(f"Interest over time for '{keyword}'" if language.startswith('en') else f"Интерес с течением времени по запросу '{keyword}'", fontsize=16)
    plt.legend()
    plt.xlabel('Date' if language.startswith('en') else 'Дата', fontsize=12)
    plt.ylabel('Interest' if language.startswith('en') else 'Интерес', fontsize=12)

    # Форматирование оси X для отображения месяцев
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Отображать каждый месяц
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Формат: 'Jan 2023'

    plt.xticks(rotation=45)  # Поворот меток даты для лучшей читаемости
    plt.grid(True)  # Добавление сетки

    plt.tight_layout()  # Автоматическое расположение элементов

    # Сохранение графика
    chart_path = 'google_trends.png'
    plt.savefig(chart_path)
    plt.close()

    return chart_path


# Обработчик команды /google
@dp.message(Command(commands=['google']))
async def send_google_trends(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        language = get_user_language(message.from_user.id)  # Предполагается, что функция синхронная
        is_russian = (language == 'ru')

        # Получаем ключевую фразу из сообщения
        query = message.text[len('/google'):].strip()
        if not query:
            if is_russian:
                await message.reply("❗️ Пожалуйста, введите ключевые слова для поиска после команды. Например: /google Bitcoin price")
            else:
                await message.reply("❗️ Please enter keywords for search after the command. For example: /google Bitcoin price")
            return

        # Проверяем, что ключевая фраза содержит только допустимые символы (буквы, цифры, пробелы)
        if not all(c.isalnum() or c.isspace() for c in query):
            if is_russian:
                await message.reply("❗️ Ключевые слова должны содержать только буквы, цифры и пробелы.")
            else:
                await message.reply("❗️ Keywords must contain only letters, numbers, and spaces.")
            return

        keyword = query
        # Получаем данные и строим график
        chart_path = get_google_trends(keyword, language='ru-RU' if is_russian else 'en-US')

        if chart_path:
            # Определяем подпись к изображению
            caption = "Google Trends 📊"

            # Отправляем изображение пользователю с локализованным заголовком
            await message.answer_photo(FSInputFile(chart_path), caption=caption)

            # Опционально: удаление файла после отправки
            os.remove(chart_path)
        else:
            if is_russian:
                await message.reply("❌ Не удалось получить данные по введённым ключевым словам.")
            else:
                await message.reply("❌ Failed to retrieve data for the specified keywords.")
            return

    except Exception as e:
        # В случае ошибки отправляем сообщение на нужном языке
        error_message = (
            "⚠️ An error occurred while fetching Google Trends data. Please try again later." if not is_russian
            else "⚠️ Произошла ошибка при получении данных Google Trends. Пожалуйста, попробуйте позже."
        )
        await message.reply(error_message)
        print(f"Ошибка: {e}")


