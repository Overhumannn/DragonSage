# Базовый образ Python
FROM python:3.9-slim-buster

# Установка необходимых системных пакетов, включая PostgreSQL и Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    curl \
    wget \
    ffmpeg \
    postgresql \
    postgresql-contrib \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Установка переменных окружения (замените на ваши значения или используйте ARG)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DB_USER=${db_user} \
    DB_PASSWORD=${db_password} \
    DB_NAME=${db_name}

# Создание рабочего каталога
WORKDIR /app

# Копирование файла зависимостей и установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего кода приложения
COPY . .

# Копирование конфигурации Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Инициализация базы данных PostgreSQL
RUN service postgresql start && \
    su postgres -c "psql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';\"" && \
    su postgres -c "psql -c \"CREATE DATABASE $DB_NAME OWNER $DB_USER;\"" && \
    service postgresql stop

# Создание директорий для логов Supervisor
RUN mkdir -p /var/log/postgresql /var/log/bot

# Экспорт порта (если необходимо)
EXPOSE 8080

# Запуск Supervisor
CMD ["/usr/bin/supervisord"]
