from aiogram import types
from aiogram.filters import Command
from bot import dp

# Set language command
@dp.message(Command(commands=['language']))
async def set_language(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton(text="English", callback_data="lang_en")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.reply("Выберите язык / Choose a language:", reply_markup=keyboard)