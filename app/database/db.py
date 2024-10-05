import time
import psycopg2
from config import settings  # Импорт настроек для подключения к базе данных
import logging

logger = logging.getLogger(__name__)

def get_db_connection(retries=5, delay=5):
    connection = None
    for attempt in range(retries):
        try:
            connection = psycopg2.connect(
                host=settings.db_host,
                port=settings.db_port,
                user=settings.db_user,
                password=settings.db_password,
                dbname=settings.db_name
            )
            return connection
        except psycopg2.OperationalError as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
                logger.info(f"Повторная попытка подключения ({attempt + 2} из {retries})...")
            else:
                raise e
