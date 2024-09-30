from services.utils import get_language  # Импорт функции для получения языка
from locales import languages  # Импорт локалей

# Translate text based on user language
async def translate(text_key, user_id):
    language_code = await get_language(user_id)
    print(f"Translating {text_key} to {language_code}")
    return languages[language_code].get(text_key, text_key)