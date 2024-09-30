from aiogram import Bot, Dispatcher
from config import settings

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()  # Создаем диспетчер без аргументов

# Привязка диспетчера к боту будет выполнена при регистрации обработчиков
__all__ = ['bot', 'dp']
