# app/bot/handlers/callbacks.py

from aiogram import types
from bot import dp
from app.database.crud import set_user_language

# Обработка выбора языка
@dp.callback_query(lambda callback_query: callback_query.data.startswith('lang_'))
async def process_language(callback_query: types.CallbackQuery):
    # Извлекаем код языка из callback_data
    language_code = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id

    # Сохраняем выбранный язык в базе данных
    set_user_language(user_id, language_code)

    # Отправляем подтверждение пользователю
    if language_code == 'ru':
        await callback_query.message.answer("Язык изменен")
    else:
        await callback_query.message.answer("Language changed")

    # Отвечаем на callback, чтобы убрать "loading" на кнопке
    await callback_query.answer()

