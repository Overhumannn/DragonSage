
import json
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    telegram_bot_token: str
    crypto_api_key: str
    db_host: str
    db_port: str 
    db_user: str 
    db_password: str 
    db_name: str 
    binance_api_key: str  # Binance API Key
    binance_api_secret: str  # Binance API Secret Key (optional)
    openai_api_key: str  # OpenAI API Key
    newsdata_api_key: str  # Newsdata API Key
    opensea_api_key: str  # OpenSea API Key
    pythonpath: str  # Python path
    coindar_api: str  # Coindar API
    bitget_api_key: str  # Bitget API Key
    bitget_secret_api_key: str  # Bitget Secret API Key
    thegraph_api_key: str
    tron_api_key: str
    etherscan_api_key:str

    class Config:
        env_file = ".env"

def load_language(lang_code, base_dir):
    locale_path = os.path.join(base_dir, f"{lang_code}.json")
    with open(locale_path, 'r', encoding='utf-8') as file:
        return json.load(file)

settings = Settings()
