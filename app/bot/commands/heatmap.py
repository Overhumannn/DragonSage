import os  # Для работы с файловой системой (удаление файлов)
import time  # Для работы с задержками (time.sleep)
from selenium import webdriver  # Для работы с Selenium WebDriver
from selenium.webdriver.chrome.service import Service  # Для создания службы ChromeDriver
from selenium.webdriver.common.by import By  # Для поиска элементов на странице
from selenium.webdriver.chrome.options import Options  # Для настройки опций Chrome
from aiogram import types  # Для работы с типами данных Telegram
from aiogram.filters import Command  # Для фильтрации команд
from aiogram.types import Message, FSInputFile  # Для обработки сообщений Telegram и отправки файлов
from bot import dp  # Для доступа к диспетчеру вашего бота
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя
import asyncio  # Для асинхронных операций
import logging  # Для логирования

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Selenium WebDriver setup
def get_heatmap_screenshot():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    # Используйте переменные окружения для пути к chromedriver
    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', 'C:/chromedriver/chromedriver.exe')
    service = Service(chromedriver_path)  # Укажите путь к вашему chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Открываем страницу с виджетом
        driver.get("https://coin360.com/widget/map?utm_source=embed_map")
        time.sleep(5)  # Ждем загрузки страницы

        # Находим элемент виджета по его CSS-селектору и делаем скриншот
        element = driver.find_element(By.CSS_SELECTOR, "body")
        element_png = element.screenshot_as_png

        # Сохраняем скриншот
        with open("heatmap.png", "wb") as file:
            file.write(element_png)

    finally:
        driver.quit()

    return "heatmap.png"

# Обработчик команды /heatmap и /тепловая_карта
@dp.message(Command(commands=['heatmap']))
async def send_heatmap(message: Message):
    try:
        # Получаем язык пользователя из базы данных
        language = get_user_language(message.from_user.id)  # Предполагается, что функция синхронная
        is_russian = (language == 'ru')

        # Запуск блокирующей функции в отдельном потоке
        heatmap_path = await asyncio.to_thread(get_heatmap_screenshot)

        # Определяем подпись к изображению на основе языка
        caption = "📈 **Cryptocurrency Heatmap**" if not is_russian else "📈 **Тепловая карта криптовалют**"

        # Отправляем изображение пользователю с локализованной подписью
        await message.answer_photo(FSInputFile(heatmap_path), caption=caption, parse_mode="Markdown")

        # Опционально: удаление файла после отправки
        os.remove(heatmap_path)

    except Exception as e:
        # В случае ошибки отправляем сообщение на нужном языке
        if 'is_russian' in locals() and is_russian:
            await message.reply("⚠️ Произошла ошибка при построении тепловой карты.")
        else:
            await message.reply("⚠️ An error occurred while generating the heatmap.")
        logger.error(f"Ошибка: {e}")
