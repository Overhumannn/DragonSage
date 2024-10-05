# 1. Укажите базовый образ Python с минимальным набором инструментов
FROM python:3.9-slim-buster

# 2. Обновите систему и установите необходимые системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Создайте директорию для вашего приложения внутри контейнера
WORKDIR /app

# 4. Скопируйте файл зависимостей requirements.txt в контейнер
COPY requirements.txt .

# 5. Установите зависимости Python и удалите кеш pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Скопируйте все файлы вашего проекта в рабочую директорию контейнера
COPY . .

# 7. Установите переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 8. Определите команду для запуска вашего бота
CMD ["python", "app/main.py"]
