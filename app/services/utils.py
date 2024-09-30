from database.crud import get_user_language  # Импортируем функцию из crud.py

# Fetch language for a user
async def get_language(user_id):
    language_code = get_user_language(user_id)
    print(f"Language for user {user_id}: {language_code}")
    return language_code