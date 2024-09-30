import requests
import datetime
import logging
from aiogram import types, Bot
from aiogram.utils.markdown import link
from config import settings  # Подключаем настройки
from bot import dp
from app.database.crud import get_user_language
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MAX_EVENTS = 30  # Максимальное количество событий
MAX_MESSAGE_LENGTH = 4096  # Максимальная длина сообщения в Telegram

# Эмодзи для разных типов событий
EVENT_EMOJIS = {
    "4": "🎁",  # Giveaway
    "5": "💸",  # Airdrop
    "8": "💻",  # Hackathon
    "15": "🛠",  # Upgrade
    "6": "🔥",  # Token Burn
    "19": "🔧",  # Mainnet Upgrade
    "22": "📞",  # Community Call
    "2": "🎤",  # AMA on X
    "9": "📉",  # Delisting
    "17": "🔄",  # Token Swap
    "23": "📈",  # Listing
    "21": "🏆",  # Конференции
}

# Кэш для хранения списка криптовалют
COINS_CACHE = {}

# Функция для загрузки списка криптовалют
def load_coins():
    global COINS_CACHE
    try:
        response = requests.get(
            "https://coindar.org/api/v2/coins",
            params={
                "access_token": settings.coindar_api
            }
        )
        if response.status_code == 200:
            coins_data = response.json()
            COINS_CACHE = {coin['id']: coin['symbol'] for coin in coins_data}
            logging.info(f"Загружено {len(COINS_CACHE)} криптовалют.")
        else:
            logging.error(f"Ошибка при загрузке списка криптовалют: {response.status_code}")
    except Exception as e:
        logging.error(f"Ошибка при загрузке списка криптовалют: {e}")

# Функция для получения символа токена по coin_id
def get_coin_symbol(coin_id):
    if not COINS_CACHE:
        load_coins()  # Загружаем кэш, если он пустой
    return COINS_CACHE.get(str(coin_id), "Unknown")  # Преобразуем coin_id в строку и возвращаем символ

# Функция для обработки форматов даты
def parse_event_date(date_str):
    formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    logging.error(f"Ошибка при преобразовании даты: {date_str}")
    return None

# Обработчик команды /events
@dp.message(Command(commands=['events']))
async def events_handler(message: types.Message, bot: Bot):
    today = datetime.datetime.utcnow()
    today_str = today.strftime('%Y-%m-%d')
    user_language = get_user_language(message.from_user.id)

    logging.info(f"Получаем актуальные события на дату: {today_str}")

    # Делаем запрос к API Coindar для событий
    try:
        response = requests.get(
            "https://coindar.org/api/v2/events",
            params={
                "access_token": settings.coindar_api,
                "filter_date_start": today_str,
                "page_size": MAX_EVENTS
            }
        )
    except Exception as e:
        logging.error(f"Ошибка при выполнении запроса к API: {e}")
        await message.answer("Ошибка при запросе данных.")
        return

    logging.info(f"Ответ от API Coindar: {response.status_code}")
    if response.status_code != 200:
        await message.answer("Ошибка при запросе данных.")
        return

    data = response.json()
    logging.info(f"Полученные данные от API: {data}")

    # Фильтрация данных для отображения только актуальных событий
    filtered_data = []
    for event in data:
        event_date_start_str = event.get("date_start", "")
        event_date_start = parse_event_date(event_date_start_str)

        # Фильтруем события, которые начинаются до сегодняшнего дня
        if event_date_start and event_date_start >= today:
            filtered_data.append(event)

    # Сортировка по дате начала (от ближайших к самым поздним)
    filtered_data.sort(key=lambda x: parse_event_date(x.get("date_start", "")) or today)

    if not filtered_data:
        logging.info(f"Нет актуальных данных для даты: {today_str}")
        if user_language == 'ru':
            await message.answer("❗️ На сегодня нет актуальных событий.")
        else:
            await message.answer("❗️ No current events for today.")
        return

    # Адаптация заголовка с жирным шрифтом
    if user_language == 'ru':
        today_title = "**Актуальные события**:"
    else:
        today_title = "**Current Events**:"

    event_messages = [today_title]

    # Ограничиваем размер сообщения, выводя только ключевые данные
    for event in filtered_data:
        event_date_start_str = event.get("date_start", "")
        event_caption = event.get("caption", "Unknown Event")
        event_source = event.get("source", "#")
        event_link = link(event_caption, event_source)
        event_tags = event.get("tags", "")
        coin_id = event.get("coin_id", None)

        # Получаем символ токена по coin_id
        coin_symbol = get_coin_symbol(coin_id) if coin_id else "Unknown"

        # Преобразуем строку даты в объект datetime
        event_date_start = parse_event_date(event_date_start_str)
        if not event_date_start:
            continue  # Пропускаем события с некорректной датой начала

        # Находим соответствующий эмодзи по тегам
        emoji = "⚡"  # Замена эмодзи на молнию
        for tag in event_tags.split(","):
            if tag in EVENT_EMOJIS:
                emoji = EVENT_EMOJIS[tag]
                break

        # Формат сообщения: символ криптовалюты и ссылка на событие
        event_message = f"{emoji} {event_date_start.date()} | {coin_symbol} | {event_caption}: {event_link}"
        event_messages.append(event_message)

        # Если длина сообщений близка к лимиту, отправляем сообщение
        if len("\n".join(event_messages)) > MAX_MESSAGE_LENGTH:
            await message.answer("\n".join(event_messages), parse_mode="Markdown", disable_web_page_preview=True)
            event_messages = [today_title]  # Обнуляем для следующей порции сообщений

    # Отправляем оставшиеся сообщения
    if len(event_messages) > 1:
        await message.answer("\n".join(event_messages), parse_mode="Markdown", disable_web_page_preview=True)
