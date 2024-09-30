# db.py
import psycopg2
from config import settings  # Импорт настроек для подключения к базе данных

def get_db_connection():
    connection = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        dbname=settings.db_name
    )
    return connection
