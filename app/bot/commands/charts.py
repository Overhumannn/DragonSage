import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import aiohttp
import os
import re
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from bot import dp
from config import settings
from app.database.crud import get_user_language  # Импортируем функцию для получения языка пользователя

# Словарь сообщений на разных языках
messages = {
    'ru': {
        'no_symbol': "Пожалуйста, укажите символ криптовалюты.",
        'invalid_interval_format': "Неверный формат интервала. Пожалуйста, используйте один из следующих: 1м, 5м, 15м, 30м, 1ч, 4ч, 1д, 3д, 1н, 1М",
        'invalid_interval': "Неверный интервал. Пожалуйста, используйте один из следующих: 1м, 5м, 15м, 30м, 1ч, 4ч, 1д, 3д, 1н, 1М",
        'data_error': "Не удалось получить корректные данные для построения графика.",
        'error': "Произошла ошибка при получении данных или построении графика.",
        'chart_caption': "{symbol} График свечей"
    },
    'en': {
        'no_symbol': "Please specify a cryptocurrency symbol.",
        'invalid_interval_format': "Invalid interval format. Please use one of the following: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 3d, 1w, 1M",
        'invalid_interval': "Invalid interval. Please use one of the following: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 3d, 1w, 1M",
        'data_error': "Failed to retrieve valid data for charting.",
        'error': "An error occurred while fetching data or generating the chart.",
        'chart_caption': "{symbol} Candlestick Chart"
    }
}

# Функция для получения данных с CryptoCompare
async def get_cryptocompare_data(symbol, interval='histoday', limit=200):
    url = f"https://min-api.cryptocompare.com/data/{interval}?fsym={symbol}&tsym=USD&limit={limit}&api_key={settings.crypto_api_key}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if response.status != 200 or 'Data' not in data:
                return None

            # Преобразуем данные в DataFrame
            df = pd.DataFrame(data['Data'])
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Переименовываем колонку "volumefrom" в "volume"
            df.rename(columns={'volumefrom': 'volume'}, inplace=True)
            return df[['open', 'high', 'low', 'close', 'volume']]

# Построение и сохранение увеличенного графика
def plot_chart(data, symbol, user_language):
    # Устанавливаем стиль свечей: зеленые для роста и красные для падения
    mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)

    # Локализация заголовков осей
    ylabel = 'Price (USD)' if user_language == 'en' else 'Цена (USD)'
    ylabel_lower = 'Volume' if user_language == 'en' else 'Объем'

    # Строим график со свечами и объемом
    fig, axlist = mpf.plot(
        data,
        type='candle',
        style=s,
        title=f'{symbol} {messages[user_language]["chart_caption"].format(symbol=symbol)}',
        ylabel=ylabel,
        ylabel_lower=ylabel_lower,
        volume=True,
        figratio=(16, 9),  # Соотношение сторон
        figscale=1.5,  # Увеличение масштаба графика
        returnfig=True
    )

    # Сохранение графика в файле с высоким разрешением
    chart_path = f"{symbol}_candlestick_chart.png"
    fig.savefig(chart_path, dpi=300)  # Увеличиваем разрешение
    plt.close(fig)  # Закрываем график после сохранения
    return chart_path

# Функция для получения endpoint и limit на основе интервала
def get_endpoint_and_limit(num, unit):
    if unit in ['м', 'm']:  # минуты
        endpoint = 'histominute'
        limit = max(num * 2, 30)  # Получаем минимум 30 точек данных
    elif unit in ['ч', 'h']:  # часы
        if num <= 4:
            endpoint = 'histominute'
            limit = num * 60
        else:
            endpoint = 'histohour'
            limit = num
    elif unit in ['д', 'd']:  # дни
        endpoint = 'histohour'
        limit = num * 24
    elif unit in ['н', 'w']:  # недели
        endpoint = 'histohour'
        limit = num * 168  # 168 часов в неделе
    elif unit == 'М' or unit == 'M':  # месяцы
        endpoint = 'histoday'
        limit = num * 30
    else:
        return None, None

    limit = min(limit, 2000)
    limit = max(limit, 30)  # Минимум 30 точек данных

    return endpoint, limit

# Обработчик команды /charts
@dp.message(Command(commands=['charts']))
async def send_chart(message: Message):
    # Получаем язык пользователя
    user_language = get_user_language(message.from_user.id) or 'en'

    args = message.text.split()
    if len(args) < 2:
        await message.answer(messages[user_language]['no_symbol'])
        return

    symbol = args[1].upper().strip()

    if len(args) >= 3:
        interval_input = args[2]
    else:
        interval_input = '1ч' if user_language == 'ru' else '1h'  # По умолчанию 1 час

    # Поддержка интервалов на обоих языках
    interval_pattern = r'^(\d+)([мчднМmhdwM])$'
    match = re.match(interval_pattern, interval_input)
    if not match:
        await message.answer(messages[user_language]['invalid_interval_format'])
        return

    num = int(match.group(1))
    unit = match.group(2)

    endpoint, limit = get_endpoint_and_limit(num, unit)
    if endpoint is None:
        await message.answer(messages[user_language]['invalid_interval'])
        return

    try:
        # Получаем данные с CryptoCompare
        data = await get_cryptocompare_data(symbol, interval=endpoint, limit=limit)

        # Проверяем, что это DataFrame и содержит нужные данные
        if isinstance(data, pd.DataFrame) and 'close' in data.columns:
            # Строим график и сохраняем его
            chart_path = plot_chart(data, symbol, user_language)

            # Отправляем график пользователю
            await message.answer_photo(FSInputFile(chart_path), caption=messages[user_language]['chart_caption'].format(symbol=symbol))

            # Удаление файла после отправки
            os.remove(chart_path)
        else:
            await message.answer(messages[user_language]['data_error'])

    except Exception as e:
        await message.answer(messages[user_language]['error'])
        print(f"Ошибка: {e}")
