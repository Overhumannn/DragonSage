import psycopg2
from config import settings  # Импорт настроек для подключения к базе данных
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection(retry_attempts=5, retry_delay=5):
    for attempt in range(retry_attempts):
        try:
            connection = psycopg2.connect(
                host=settings.db_host,
                port=settings.db_port,
                user=settings.db_user,
                password=settings.db_password,
                dbname=settings.db_name,
                connect_timeout=10  # Устанавливаем тайм-аут подключения (в секундах)
            )
            logger.info("Успешное подключение к базе данных.")
            return connection
        except psycopg2.OperationalError as e:
            logger.error(f"Ошибка подключения к базе данных: {e}. Попытка {attempt + 1} из {retry_attempts}.")
            if attempt < retry_attempts - 1:
                time.sleep(retry_delay)
            else:
                raise e
