import json
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Загружаем переменные окружения из .env файла
load_dotenv()

class Settings(BaseSettings):
    telegram_bot_token: str = os.getenv("telegram_bot_token", "")
    crypto_api_key: str = os.getenv("crypto_api_key", "")
    db_host: str = os.getenv("db_host", "localhost")
    db_port: str = os.getenv("db_port", "5432")
    db_user: str = os.getenv("db_user", "")
    db_password: str = os.getenv("db_password", "")
    db_name: str = os.getenv("db_name", "")
    binance_api_key: str = os.getenv("binance_api_key", "")
    binance_api_secret: str = os.getenv("binance_api_secret", "")
    openai_api_key: str = os.getenv("openai_api_key", "")
    newsdata_api_key: str = os.getenv("newsdata_api_key", "")
    opensea_api_key: str = os.getenv("opensea_api_key", "")
    pythonpath: str = os.getenv("pythonpath", "")
    coindar_api: str = os.getenv("coindar_api", "")
    bitget_api_key: str = os.getenv("bitget_api_key", "")
    bitget_secret_api_key: str = os.getenv("bitget_secret_api_key", "")
    thegraph_api_key: str = os.getenv("thegraph_api_key", "")
    tron_api_key: str = os.getenv("tron_api_key", "")
    etherscan_api_key: str = os.getenv("etherscan_api_key", "")

    class Config:
        env_file = ".env"

# Функция для загрузки языковых настроек
def load_language(lang_code, base_dir):
    locale_path = os.path.join(base_dir, f"{lang_code}.json")
    with open(locale_path, 'r', encoding='utf-8') as file:
        return json.load(file)

settings = Settings()
