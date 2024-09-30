# app/database/crud.py

from .db import get_db_connection
from psycopg2.extras import RealDictCursor
# Импортируем сессию из модуля базы данных
from app.database.db import get_db_connection  # Импортируем функцию для получения подключения к базе данных


# Функция для установки языка пользователя
def set_user_language(telegram_id, language):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO users (telegram_id, language)
        VALUES (%s, %s)
        ON CONFLICT (telegram_id) DO UPDATE
        SET language = EXCLUDED.language;
    """, (telegram_id, language))
    connection.commit()
    cursor.close()
    connection.close()

# Функция для получения языка пользователя
def get_user_language(telegram_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT language FROM users WHERE telegram_id = %s;", (telegram_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result['language'] if result else 'ru'  # Язык по умолчанию - русский

# Функция для добавления подписки
def add_subscription(telegram_id, collection_slug, event_type):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO subscriptions (telegram_id, collection_slug, event_type)
        VALUES (%s, %s, %s)
        ON CONFLICT (telegram_id, collection_slug, event_type) DO NOTHING;
    """, (telegram_id, collection_slug, event_type))
    connection.commit()
    cursor.close()
    connection.close()

# Функция для создания новой подписки
def create_subscription(telegram_id, collection_slug, event_type):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO subscriptions (telegram_id, collection_slug, event_type)
        VALUES (%s, %s, %s)
        ON CONFLICT (telegram_id, collection_slug, event_type) DO NOTHING;
    """, (telegram_id, collection_slug, event_type))
    connection.commit()
    cursor.close()
    connection.close()


# Функция для получения активной подписки
def get_active_subscription(telegram_id, collection_slug, event_type):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT * FROM subscriptions 
        WHERE telegram_id = %s 
        AND collection_slug = %s 
        AND event_type = %s
        AND active = TRUE;
    """, (telegram_id, collection_slug, event_type))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

# Дополнительные функции по управлению подписками могут быть добавлены сюда
def get_user_language(telegram_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Получаем язык пользователя из базы данных
        cursor.execute("SELECT language FROM users WHERE telegram_id = %s", (telegram_id,))
        result = cursor.fetchone()
        if result and result[0]:
            return result[0]
        else:
            # Если язык не установлен, устанавливаем английский по умолчанию и обновляем запись
            cursor.execute("UPDATE users SET language = %s WHERE telegram_id = %s", ('en', telegram_id))
            connection.commit()
            return 'en'
    except Exception as e:
        print(f"Error fetching user language: {e}")
        return 'en'  # Возвращаем английский по умолчанию в случае ошибки
    finally:
        cursor.close()
        connection.close()

