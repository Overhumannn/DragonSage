import pandas as pd
import pandas_ta as ta
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from bot import dp
import aiohttp
import openai
from config import settings
import re
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ContentType, Voice
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
import openai
from bot import dp
import time
from langdetect import detect
import requests
import os
import speech_recognition as sr


bot = Bot(token=settings.telegram_bot_token)
openai.api_key = settings.openai_api_key

# Функция для очистки ответа от нежелательных символов
def clean_response(text):
    # Удаляем символы Markdown-разметки
    text = re.sub(r'[*#_`]', '', text)
    return text.strip()

# Функция для получения исторических данных с Binance
async def get_historical_data(symbol, interval='1h', limit=100):
    url = (
        f"https://api.binance.com/api/v3/klines?"
        f"symbol={symbol}&interval={interval}&limit={limit}"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                klines = await response.json()
                data = pd.DataFrame(
                    klines,
                    columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base_asset_volume',
                        'taker_buy_quote_asset_volume', 'ignore'
                    ]
                )
                data['close'] = data['close'].astype(float)
                data['high'] = data['high'].astype(float)
                data['low'] = data['low'].astype(float)
                data['volume'] = data['volume'].astype(float)
                return data
            else:
                raise Exception(f"Ошибка при получении данных: {response.status}")

# Функция для получения текущей цены и объёма за последний час
async def get_current_price_and_hourly_volume(symbol):
    data = await get_historical_data(symbol, interval='1h', limit=1)
    price = data['close'].iloc[-1]
    volume = data['volume'].iloc[-1]
    return price, volume

# Функция для расчёта и получения технических индикаторов
async def get_technical_indicators(symbol):
    data = await get_historical_data(symbol)
    price, volume = await get_current_price_and_hourly_volume(symbol)

    # Расчёт средней волатильности (ATR / close price * 100) для процента
    atr_value = ta.atr(
        data['high'], data['low'], data['close'], length=14
    ).iloc[-1]
    avg_volatility = (atr_value / data['close'].iloc[-1]) * 100

    # Расчёт других индикаторов
    rsi_value = ta.rsi(data['close'], length=14).iloc[-1]
    mfi_value = ta.mfi(
        data['high'], data['low'], data['close'],
        data['volume'].astype('float64'), length=14
    ).iloc[-1]
    cci_value = ta.cci(
        data['high'], data['low'], data['close'], length=14
    ).iloc[-1]
    macd = ta.macd(
        data['close'], fast=12, slow=26, signal=9
    )
    macd_value = macd['MACD_12_26_9'].iloc[-1]
    adx = ta.adx(
        data['high'], data['low'], data['close'], length=14
    )
    adx_value = adx['ADX_14'].iloc[-1]

    # Полосы Боллинджера
    bbands = ta.bbands(
        data['close'], length=20, std=2
    ).iloc[-1]
    bbands_lower = bbands['BBL_20_2.0']
    bbands_middle = bbands['BBM_20_2.0']
    bbands_upper = bbands['BBU_20_2.0']

    # Скользящая средняя
    sma_50 = ta.sma(data['close'], length=50).iloc[-1]

    indicators = {
        "Price": price,
        "Volume": volume,
        "AvgVolatility": avg_volatility,
        "RSI": rsi_value,
        "MFI": mfi_value,
        "CCI": cci_value,
        "BBands_Lower": bbands_lower,
        "BBands_Middle": bbands_middle,
        "BBands_Upper": bbands_upper,
        "SMA": sma_50,
        "MACD": macd_value,
        "ADX": adx_value,
    }

    # Определение тренда
    indicators["Trend"] = (
        "Бычий" if indicators["MACD"] > 0 and indicators["ADX"] > 25
        else "Медвежий"
    )

    return indicators

# Функция для генерации анализа с помощью OpenAI GPT
async def generate_gpt_analysis(indicators, symbol, is_russian):
    # Создаем промпт на основе языка пользователя
    if is_russian:
        prompt = (
            f"Вы являетесь экспертом в области технического анализа криптовалют.\n"
            f"На основе следующих технических индикаторов для {symbol} предоставьте подробный анализ текущего состояния рынка и дайте рекомендации для трейдеров.\n"
            "Пожалуйста, представьте ваш ответ в виде простого текста без использования каких-либо форматов или Markdown-разметки. Но в то же время ответ должен иметь структуру, пункты и ОБЯЗАТЕЛЬНО используйте эмодзи для визуализации. В самом конце своего вывода добавьте фразу 'Не является профессиональной рекомендацией'.\n\n"
            "Технические индикаторы:\n"
            f"Цена: {indicators['Price']:.2f} USDT\n"
            f"Объём: {indicators['Volume']:.2f}\n"
            f"Средняя Волатильность (ATR): {indicators['AvgVolatility']:.2f}%\n"
            f"RSI (14): {indicators['RSI']:.2f}\n"
            f"MFI (14): {indicators['MFI']:.2f}\n"
            f"CCI (14): {indicators['CCI']:.2f}\n"
            f"Полосы Боллинджера (20,2):\n"
            f"  Нижняя: {indicators['BBands_Lower']:.2f}\n"
            f"  Средняя: {indicators['BBands_Middle']:.2f}\n"
            f"  Верхняя: {indicators['BBands_Upper']:.2f}\n"
            f"SMA (50): {indicators['SMA']:.2f}\n"
            f"MACD: {indicators['MACD']:.2f}\n"
            f"ADX (14): {indicators['ADX']:.2f}\n"
            f"Тренд: {indicators['Trend']}\n"
        )
        system_content = "Вы являетесь экспертом по техническому анализу криптовалют."
    else:
        prompt = (
            f"You are an expert in cryptocurrency technical analysis.\n"
            f"Based on the following technical indicators for {symbol}, provide a detailed analysis of the current market condition and give recommendations for traders.\n"
            "Please present your answer as plain text without using any formatting or Markdown. Ensure the answer has structure, bullet points, and USE EMOJIES for visualization. At the very end of your response, add the phrase 'This is not financial advice.'\n\n"
            "Technical Indicators:\n"
            f"Price: {indicators['Price']:.2f} USDT\n"
            f"Volume: {indicators['Volume']:.2f}\n"
            f"Average Volatility (ATR): {indicators['AvgVolatility']:.2f}%\n"
            f"RSI (14): {indicators['RSI']:.2f}\n"
            f"MFI (14): {indicators['MFI']:.2f}\n"
            f"CCI (14): {indicators['CCI']:.2f}\n"
            f"Bollinger Bands (20,2):\n"
            f"  Lower: {indicators['BBands_Lower']:.2f}\n"
            f"  Middle: {indicators['BBands_Middle']:.2f}\n"
            f"  Upper: {indicators['BBands_Upper']:.2f}\n"
            f"SMA (50): {indicators['SMA']:.2f}\n"
            f"MACD: {indicators['MACD']:.2f}\n"
            f"ADX (14): {indicators['ADX']:.2f}\n"
            f"Trend: {indicators['Trend']}\n"
        )
        system_content = "You are an expert in cryptocurrency technical analysis."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )

        analysis = response['choices'][0]['message']['content']
        # Очищаем ответ от нежелательных символов
        cleaned_analysis = clean_response(analysis)
        return cleaned_analysis

    except openai.error.OpenAIError as e:
        print(f"Ошибка OpenAI API: {e}")
        if is_russian:
            return "Произошла ошибка при попытке получить анализ с помощью AI."
        else:
            return "An error occurred while trying to get analysis using AI."

# Обработчик команды /aita
@dp.message(Command(commands=['aita']))
async def send_ai_technical_analysis(message: Message):
    # Получаем язык пользователя
    language = get_user_language(message.from_user.id)
    is_russian = (language == 'ru')

    if len(message.text.split()) < 2:
        if is_russian:
            await message.reply(
                "Пожалуйста, укажите символ криптовалюты. Пример использования: /aita BTC"
            )
        else:
            await message.reply(
                "Please specify the cryptocurrency symbol. Usage example: /aita BTC"
            )
        return

    symbol = message.text.split(' ')[1].upper() + 'USDT'

    try:
        # Получаем технические индикаторы
        indicators = await get_technical_indicators(symbol)

        # Генерируем анализ с помощью GPT
        analysis = await generate_gpt_analysis(indicators, symbol, is_russian)

        # Отправляем сообщение без форматирования и эмодзи
        await message.answer(analysis)

    except Exception as e:
        if is_russian:
            await message.reply(
                "Произошла ошибка при получении данных или генерации анализа."
            )
        else:
            await message.reply(
                "An error occurred while fetching data or generating analysis."
            )
        print(f"Ошибка: {e}")

# Функция для генерации торговой стратегии с помощью OpenAI GPT для команды /aistrat
async def generate_gpt_strategy(indicators, symbol, is_russian):
    if is_russian:
        prompt = (
            f"Вы являетесь экспертом по торговым стратегиям в области криптовалют.\n"
            f"На основе следующих технических индикаторов для {symbol} разработайте персонализированную торговую стратегию, учитывающую движение цен и текущие рыночные условия.\n"
            "Пожалуйста, представьте ваш ответ в виде простого текста без использования каких-либо форматов или Markdown-разметки. Ответ должен содержать четкую структуру и рекомендации, ОБЯЗАТЕЛЬНО добавляйте эмодзи для персонализации и визуализации. В конце вашего вывода добавьте фразу 'Не является профессиональной рекомендацией'.\n\n"
            "Технические индикаторы:\n"
            f"Цена: {indicators['Price']:.2f} USDT\n"
            f"Объём: {indicators['Volume']:.2f}\n"
            f"Средняя Волатильность (ATR): {indicators['AvgVolatility']:.2f}%\n"
            f"RSI (14): {indicators['RSI']:.2f}\n"
            f"MFI (14): {indicators['MFI']:.2f}\n"
            f"CCI (14): {indicators['CCI']:.2f}\n"
            f"Полосы Боллинджера (20,2):\n"
            f"  Нижняя: {indicators['BBands_Lower']:.2f}\n"
            f"  Средняя: {indicators['BBands_Middle']:.2f}\n"
            f"  Верхняя: {indicators['BBands_Upper']:.2f}\n"
            f"SMA (50): {indicators['SMA']:.2f}\n"
            f"MACD: {indicators['MACD']:.2f}\n"
            f"ADX (14): {indicators['ADX']:.2f}\n"
            f"Тренд: {indicators['Trend']}\n"
        )
        system_content = "Вы являетесь экспертом по торговым стратегиям в области криптовалют."
    else:
        prompt = (
            f"You are an expert in cryptocurrency trading strategies.\n"
            f"Based on the following technical indicators for {symbol}, develop a personalized trading strategy that considers price movements and current market conditions.\n"
            "Please present your answer as plain text without using any formatting or Markdown. The answer should have a clear structure and recommendations, MAKE SURE to add emojis for personalization and visualization. At the end of your response, add the phrase 'This is not financial advice.'\n\n"
            "Technical Indicators:\n"
            f"Price: {indicators['Price']:.2f} USDT\n"
            f"Volume: {indicators['Volume']:.2f}\n"
            f"Average Volatility (ATR): {indicators['AvgVolatility']:.2f}%\n"
            f"RSI (14): {indicators['RSI']:.2f}\n"
            f"MFI (14): {indicators['MFI']:.2f}\n"
            f"CCI (14): {indicators['CCI']:.2f}\n"
            f"Bollinger Bands (20,2):\n"
            f"  Lower: {indicators['BBands_Lower']:.2f}\n"
            f"  Middle: {indicators['BBands_Middle']:.2f}\n"
            f"  Upper: {indicators['BBands_Upper']:.2f}\n"
            f"SMA (50): {indicators['SMA']:.2f}\n"
            f"MACD: {indicators['MACD']:.2f}\n"
            f"ADX (14): {indicators['ADX']:.2f}\n"
            f"Trend: {indicators['Trend']}\n"
        )
        system_content = "You are an expert in cryptocurrency trading strategies."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,  # Увеличиваем лимит токенов для более детальной стратегии
            temperature=0.5
        )

        strategy = response['choices'][0]['message']['content']
        # Очищаем ответ от нежелательных символов
        cleaned_strategy = clean_response(strategy)
        return cleaned_strategy

    except openai.error.OpenAIError as e:
        print(f"Ошибка OpenAI API: {e}")
        if is_russian:
            return "Произошла ошибка при попытке получить торговую стратегию с помощью AI."
        else:
            return "An error occurred while trying to get a trading strategy using AI."

# Обработчик команды /aistrat
@dp.message(Command(commands=['aistrat']))
async def send_ai_trading_strategy(message: Message):
    # Получаем язык пользователя
    language = get_user_language(message.from_user.id)
    is_russian = (language == 'ru')

    if len(message.text.split()) < 2:
        if is_russian:
            await message.reply(
                "Пожалуйста, укажите символ криптовалюты. Пример использования: /aistrat BTC"
            )
        else:
            await message.reply(
                "Please specify the cryptocurrency symbol. Usage example: /aistrat BTC"
            )
        return

    symbol = message.text.split(' ')[1].upper() + 'USDT'

    try:
        # Получаем технические индикаторы
        indicators = await get_technical_indicators(symbol)

        # Генерируем торговую стратегию с помощью GPT
        strategy = await generate_gpt_strategy(indicators, symbol, is_russian)

        # Отправляем сообщение без форматирования и эмодзи
        await message.answer(strategy)

    except Exception as e:
        if is_russian:
            await message.reply(
                "Произошла ошибка при получении данных или генерации торговой стратегии."
            )
        else:
            await message.reply(
                "An error occurred while fetching data or generating the trading strategy."
            )
        print(f"Ошибка: {e}")

# Функция для генерации торговых сигналов с помощью OpenAI GPT
async def generate_gpt_buy_sell(indicators, symbol, is_russian):
    if is_russian:
        prompt = (
            f"Вы являетесь экспертом по торговым сигналам в области криптовалют.\n"
            f"На основе следующих технических индикаторов для {symbol} предоставьте сигналы покупки или продажи.\n"
            "Пожалуйста, представьте ваш ответ в виде простого текста без использования каких-либо форматов или Markdown-разметки. Ответ должен быть четко и строго структурирован, должен быть понятен и ОБЯЗАТЕЛЬНО содержать эмодзи для дополнительной визуализации.\n"
            "В конце вашего вывода добавьте фразу 'Не является профессиональной рекомендацией'.\n\n"
            "Технические индикаторы:\n"
            f"Цена: {indicators['Price']:.2f} USDT\n"
            f"RSI (14): {indicators['RSI']:.2f}\n"
            f"MACD: {indicators['MACD']:.2f}\n"
            f"SMA (50): {indicators['SMA']:.2f}\n"
            f"ADX (14): {indicators['ADX']:.2f}\n"
        )
        system_content = "Вы являетесь экспертом по торговым сигналам в области криптовалют."
    else:
        prompt = (
            f"You are an expert in cryptocurrency trading signals.\n"
            f"Based on the following technical indicators for {symbol}, provide buy or sell signals.\n"
            "Please present your answer as plain text without using any formatting or Markdown. The answer should be clear and strictly structured, understandable, and MUST contain emojis for additional visualization.\n"
            "At the end of your response, add the phrase 'This is not financial advice.'\n\n"
            "Technical Indicators:\n"
            f"Price: {indicators['Price']:.2f} USDT\n"
            f"RSI (14): {indicators['RSI']:.2f}\n"
            f"MACD: {indicators['MACD']:.2f}\n"
            f"SMA (50): {indicators['SMA']:.2f}\n"
            f"ADX (14): {indicators['ADX']:.2f}\n"
        )
        system_content = "You are an expert in cryptocurrency trading signals."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )

        analysis = response['choices'][0]['message']['content']
        # Очищаем ответ от нежелательных символов
        cleaned_analysis = clean_response(analysis)
        return cleaned_analysis

    except openai.error.OpenAIError as e:
        print(f"Ошибка OpenAI API: {e}")
        if is_russian:
            return "Произошла ошибка при попытке получить торговые сигналы с помощью AI."
        else:
            return "An error occurred while trying to get trading signals using AI."

# Обработчик команды /aibuysell
@dp.message(Command(commands=['aibuysell']))
async def send_buy_sell_signals(message: Message):
    # Получаем язык пользователя
    language = get_user_language(message.from_user.id)
    is_russian = (language == 'ru')

    if len(message.text.split()) < 2:
        if is_russian:
            await message.reply(
                "Пожалуйста, укажите символ криптовалюты. Пример использования: /aibuysell BTC"
            )
        else:
            await message.reply(
                "Please specify the cryptocurrency symbol. Usage example: /aibuysell BTC"
            )
        return

    symbol = message.text.split(' ')[1].upper() + 'USDT'

    try:
        # Получаем технические индикаторы
        indicators = await get_technical_indicators(symbol)

        # Генерируем торговые сигналы с помощью GPT
        buy_sell_signals = await generate_gpt_buy_sell(indicators, symbol, is_russian)

        # Отправляем сообщение без форматирования и эмодзи
        await message.answer(buy_sell_signals)

    except Exception as e:
        if is_russian:
            await message.reply(
                "Произошла ошибка при получении данных или генерации торговых сигналов."
            )
        else:
            await message.reply(
                "An error occurred while fetching data or generating trading signals."
            )
        print(f"Ошибка: {e}")




def fetch_general_crypto_news():
    # Используем API newsdata.io для поиска новостей о криптовалютах
    api_key = settings.newsdata_api_key
    # Ищем новости по ключевым словам, связанным с криптовалютами
    url = f"https://newsdata.io/api/1/news?apikey={api_key}&q=cryptocurrency,Bitcoin,Ethereum,blockchain&language=en,ru"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'success':
        articles = data['results'][:6]  # Берем последние 6 статей
        return articles
    else:
        raise Exception(f"Не удалось получить новости о криптовалютах. Причина: {data.get('message', 'Неизвестная ошибка')}")




async def analyze_news_with_gpt(news, lang):
    # Объединяем заголовки и описания новостей для анализа
    combined_text = "\n\n".join([f"{article['title']}: {article.get('description', '')}" for article in news])

    # Создаем запрос в зависимости от языка
    if lang == 'ru':
        prompt = f"""
        Очень внимательно проанализируйте последние новости и сделайте вывод по каждой из них. Пожалуйста, представьте ваш ответ в виде простого текста без использования каких-либо форматов или Markdown-разметки, в том числе знаков "**". Ответ должен содержать четкую структуру, пункты, рекомендации, ОБЯЗАТЕЛЬНО ДОБАВЬТЕ ЭМОДЗИ ДЛЯ ПЕРСОНАЛИЗАЦИИ И ВИЗУАЛИЗАЦИИ:

        {combined_text}
        """
        system_message = "Вы являетесь экспертом по анализу криптовалютного рынка."
    else:
        prompt = f"""
        Analyze the latest news very carefully and make a conclusion on each of them. Please provide your answer in plain text without any formats or Markdown including '**'. The answer should contain a clear structure, points and guidelines, BE SURE TO ADD EMOJIS FOR PERSONALIZATION AND VISUALIZATION:

        {combined_text}
        """
        system_message = "You are an expert in cryptocurrency market analysis."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Используем модель gpt-4o-mini
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )

        return response['choices'][0]['message']['content']
    except openai.error.RateLimitError:
        print("Превышены лимиты запросов. Повтор попытки через 10 секунд.")
        time.sleep(10)
        return await analyze_news_with_gpt(news, lang)
    except openai.error.InvalidRequestError as e:
        print(f"OpenAI API error: {e}")
        return "Произошла ошибка при попытке проанализировать новости." if lang == 'ru' else "An error occurred while attempting to analyze the news."
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Произошла ошибка при попытке проанализировать новости." if lang == 'ru' else "An error occurred while attempting to analyze the news."

@dp.message(Command(commands=['ainews']))
async def ainews(message: Message):
    try:
        # Получаем язык пользователя через функцию get_user_language
        lang = get_user_language(message.from_user.id)

        # Если пользователь указал язык в команде, используем его
        parts = message.text.strip().split()
        if len(parts) > 1 and parts[1].lower() in ['en', 'ru']:
            lang = parts[1].lower()

        news = fetch_general_crypto_news()
        analysis = await analyze_news_with_gpt(news, lang)
        await message.reply(analysis)

    except Exception as e:
        await message.reply(
            "Произошла ошибка при попытке получить анализ новостей." if lang == 'ru' else "An error occurred while attempting to obtain news analysis.")
        print(f"Ошибка: {e}")

# Команда для анализа аудио
async def transcribe_audio(file_path, lang):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(file_path)
    audio_chunks = make_chunks(audio, 60 * 1000)  # разбиваем аудио на 1-минутные кусочки

    full_text = ""
    for i, chunk in enumerate(audio_chunks):
        chunk_filename = f"chunk{i}.wav"
        chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_data = recognizer.record(source)
            try:
                # Определяем язык распознавания по параметру lang
                if lang == 'ru':
                    text = recognizer.recognize_google(audio_data, language="ru-RU")
                else:
                    text = recognizer.recognize_google(audio_data, language="en-US")
                full_text += text + " "
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Error with the speech recognition service: {e}")
        os.remove(chunk_filename)
    return full_text.strip()

async def analyze_voice_with_gpt(text, lang):
    if lang == "ru":
        messages = [
            {"role": "system", "content": "Вы эксперт в анализе и предоставлении советов по криптовалютам. Пожалуйста, представьте ваш ответ в виде простого текста без использования каких-либо форматов или Markdown-разметки. Ответ должен содержать четкую структуру и рекомендации, ОБЯЗАТЕЛЬНО ДОБАВЬТЕ ЭМОДЗИ ДЛЯ ПЕРСОНАЛИЗАЦИИ И ВИЗУАЛИЗАЦИИ."},
            {"role": "user", "content": f"Проанализируйте следующий текст:\n{text}"}
        ]
    else:
        messages = [
            {"role": "system", "content": "You are an expert in analyzing and providing advice on cryptocurrencies. Please provide your answer in plain text without any formats or Markdown. The answer should contain a clear structure and guidelines, BE SURE TO ADD EMOJIS FOR PERSONALIZATION AND VISUALIZATION."},
            {"role": "user", "content": f"Analyze the following text:\n{text}"}
        ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Используем модель gpt-4o-mini
            messages=messages,
            max_tokens=700,
            temperature=0.5
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Произошла ошибка при анализе текста." if lang == 'ru' else "An error occurred while attempting to analyze the text."

@dp.message(Command(commands=['aivoice']))
async def prompt_aivoice(message: Message):
    await message.reply("Please send a voice message." if get_user_language(message.from_user.id) != 'ru' else "Пожалуйста, отправьте голосовое сообщение.")

@dp.message(F.content_type == ContentType.VOICE)
async def handle_aivoice(message: Message):
    try:
        file_info = await bot.get_file(message.voice.file_id)
        file_path = f"{file_info.file_id}.ogg"

        await bot.download_file(file_info.file_path, destination=file_path)

        # Получаем язык пользователя через функцию get_user_language
        lang = get_user_language(message.from_user.id)

        text = await transcribe_audio(file_path, lang)
        os.remove(file_path)

        if not text:
            await message.reply("Could not recognize text from the voice message." if lang != 'ru' else "Не удалось распознать текст из голосового сообщения.")
            return

        # Если язык не распознан, используем язык по умолчанию
        detected_lang = detect(text)
        if detected_lang in ['en', 'ru']:
            lang = detected_lang
        else:
            lang = 'en'  # По умолчанию английский

        analysis = await analyze_voice_with_gpt(text, lang)
        await message.reply(f"Recognized text: {text}\n\nAnalysis: {analysis}" if lang != 'ru' else f"Распознанный текст: {text}\n\nАнализ: {analysis}")

    except Exception as e:
        await message.reply("An error occurred while processing the voice message." if lang != 'ru' else "Произошла ошибка при обработке голосового сообщения.")
        print(f"Ошибка: {e}")
