import pandas as pd
import pandas_ta as ta
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from bot import dp
from config import settings
import aiohttp
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя

# Функция для получения исторических данных с Binance
async def get_historical_data(symbol, interval='1h', limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                klines = await response.json()
                data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                                     'close_time', 'quote_asset_volume', 'number_of_trades',
                                                     'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                                     'ignore'])
                data['close'] = data['close'].astype(float)
                data['high'] = data['high'].astype(float)
                data['low'] = data['low'].astype(float)
                data['volume'] = data['volume'].astype(float)
                return data
            else:
                raise Exception(f"Error fetching data: {response.status}")

# Функция для получения текущей цены и объема за последний час
async def get_current_price_and_hourly_volume(symbol):
    data = await get_historical_data(symbol, interval='1h', limit=1)
    price = data['close'].iloc[-1]
    volume = data['volume'].iloc[-1]
    return price, volume

# Функция для расчета и получения технических индикаторов
async def get_technical_indicators(symbol):
    data = await get_historical_data(symbol)
    price, volume = await get_current_price_and_hourly_volume(symbol)

    # Рассчет средней волатильности (ATR / close price * 100) для процента
    atr_value = ta.atr(data['high'], data['low'], data['close'], length=14).iloc[-1]
    avg_volatility = (atr_value / data['close'].iloc[-1]) * 100

    # Рассчет других индикаторов с явным приведением volume к float64
    rsi_value = ta.rsi(data['close'], length=14).iloc[-1]
    mfi_value = ta.mfi(data['high'], data['low'], data['close'], data['volume'].astype('float64'), length=14).iloc[-1]
    cci_value = ta.cci(data['high'], data['low'], data['close'], length=14).iloc[-1]

    indicators = {
        "Price": price,
        "Volume": volume,
        "AvgVolatility": avg_volatility,
        "RSI": rsi_value,
        "MFI": mfi_value,
        "CCI": cci_value,
        "BBands": ta.bbands(data['close'], length=20, std=2).iloc[-1].tolist(),
        "SMA": ta.sma(data['close'], length=50).iloc[-1],
        "MOM": ta.mom(data['close'], length=10).iloc[-1],
        "MACD": ta.macd(data['close'], fast=12, slow=26, signal=9)['MACD_12_26_9'].iloc[-1],
        "ADX": ta.adx(data['high'], data['low'], data['close'], length=14)['ADX_14'].iloc[-1],
    }

    # Определение эмодзи на основе значений индикаторов
    if rsi_value > 70:
        rsi_emoji = "📉"  # Перекупленность
    elif rsi_value < 30:
        rsi_emoji = "📈"  # Перепроданность
    else:
        rsi_emoji = "🔄"  # Нейтральное состояние

    if mfi_value > 80:
        mfi_emoji = "💸"  # Перекупленность
    elif mfi_value < 20:
        mfi_emoji = "💹"  # Перепроданность
    else:
        mfi_emoji = "💸"  # Нейтральное состояние

    if cci_value > 100:
        cci_emoji = "📈"  # Сигнал к покупке
    elif cci_value < -100:
        cci_emoji = "📉"  # Сигнал к продаже
    else:
        cci_emoji = "🔄"  # Нейтральное состояние

    indicators["Trend"] = "📈 🐂" if indicators["MACD"] > 0 and indicators["ADX"] > 25 else "📉 🐻"

    return indicators, rsi_emoji, mfi_emoji, cci_emoji

# Обработчик команды /ta
@dp.message(Command(commands=['ta']))
async def send_technical_analysis(message: Message):
    try:
        # Получаем язык пользователя
        language = get_user_language(message.from_user.id)
        is_russian = (language == 'ru')

        if len(message.text.split()) < 2:
            if is_russian:
                await message.reply("❗️ Пожалуйста, укажите символ криптовалюты.")
            else:
                await message.reply("❗️ Please specify the cryptocurrency symbol.")
            return

        symbol = message.text.split(' ')[1].upper() + 'USDT'
        base_currency = symbol.replace('USDT', '')  # Извлекаем базовую валюту (например, BTC, ETH)

        # Получаем индикаторы и эмодзи
        indicators, rsi_emoji, mfi_emoji, cci_emoji = await get_technical_indicators(symbol)

        # Формируем ответное сообщение
        if is_russian:
            ta_message = (
                f"<b>{symbol}/USDT на Binance [1h]</b>\n"
                f"💵 <b>Цена:</b> {indicators['Price']:.2f} USDT\n"
                f"📊 <b>Объем:</b> {indicators['Volume']:.2f} {base_currency}\n\n"
                f"🔥 <b>Средняя Волатильность:</b> {indicators['AvgVolatility']:.2f}%\n"
                f"{rsi_emoji} <b>RSI(14):</b> {indicators['RSI']:.2f}\n"
                f"{mfi_emoji} <b>MFI(14):</b> {indicators['MFI']:.2f}\n"
                f"{cci_emoji} <b>CCI(14):</b> {indicators['CCI']:.2f}\n"
                f"⚠️ <b>BBands(20,2):</b> Нижняя: {indicators['BBands'][0]:.2f}, Средняя: {indicators['BBands'][1]:.2f}, Верхняя: {indicators['BBands'][2]:.2f}\n"
                f"📈 <b>SMA(50):</b> {indicators['SMA']:.2f}\n"
                f"📉 <b>MACD:</b> {indicators['MACD']:.2f}\n"
                f"📉 <b>ADX:</b> {indicators['ADX']:.2f}\n"
                f"<b>{indicators['Trend']} рынок</b>"
            )
        else:
            ta_message = (
                f"<b>{symbol}/USDT on Binance [1h]</b>\n"
                f"💵 <b>Price:</b> {indicators['Price']:.2f} USDT\n"
                f"📊 <b>Volume:</b> {indicators['Volume']:.2f} {base_currency}\n\n"
                f"🔥 <b>Avg Volatility:</b> {indicators['AvgVolatility']:.2f}%\n"
                f"{rsi_emoji} <b>RSI(14):</b> {indicators['RSI']:.2f}\n"
                f"{mfi_emoji} <b>MFI(14):</b> {indicators['MFI']:.2f}\n"
                f"{cci_emoji} <b>CCI(14):</b> {indicators['CCI']:.2f}\n"
                f"⚠️ <b>BBands(20,2):</b> Lower: {indicators['BBands'][0]:.2f}, Middle: {indicators['BBands'][1]:.2f}, Upper: {indicators['BBands'][2]:.2f}\n"
                f"📈 <b>SMA(50):</b> {indicators['SMA']:.2f}\n"
                f"📉 <b>MACD:</b> {indicators['MACD']:.2f}\n"
                f"📉 <b>ADX:</b> {indicators['ADX']:.2f}\n"
                f"<b>{indicators['Trend']} market</b>"
            )

        await message.answer(ta_message, parse_mode="HTML")  # Используем HTML для разметки

    except Exception as e:
        if is_russian:
            await message.reply("❗️ Произошла ошибка при получении данных или расчете индикаторов.")
        else:
            await message.reply("❗️ An error occurred while fetching data or calculating indicators.")
        print(f"Ошибка: {e}")
