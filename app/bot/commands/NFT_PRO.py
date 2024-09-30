import aiohttp
import asyncio
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from config import settings  # Здесь хранится ваш API-ключ
from bot import dp  # Импорт диспетчера из основного файла
import requests
from app.database.crud import create_subscription, get_user_language, add_subscription, get_active_subscription
import logging
from datetime import datetime
import websockets
import json
from app.database import crud
import subprocess


# Функция для обработки команды /nft_item_listed
@dp.message(Command(commands=['nft_item_listed']))
async def nft_item_listed_handler(message: Message):
    # Получаем коллекцию из текста сообщения
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply("❗️Please specify the collection slug after the /nft_item_listed command.")
        return

    user_id = message.from_user.id
    collection_slug = text[1].strip().lower()

    # Получаем язык пользователя из базы данных
    language = get_user_language(user_id)

    # Проверяем, существует ли уже подписка
    existing_subscription = get_active_subscription(user_id, collection_slug)
    if existing_subscription:
        await message.reply(f"❗️You are already subscribed to updates for the collection {collection_slug}.")
        return

    # Создаем новую подписку в БД
    create_subscription(user_id, collection_slug)

    try:
        # Запуск TypeScript скрипта через Node.js
        process = subprocess.Popen(['node', 'app/bot/scripts/subscribe_item_listed.js', collection_slug, str(user_id)])
        print(f"Process started with PID: {process.pid}")
        await message.reply(f"✅ Subscription to item listings in the {collection_slug} collection has been activated.")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply(f"❗️An error occurred while starting the subscription: {e}")


# Функция для обработки команды /nft_item_offer
@dp.message(Command(commands=['nft_item_offer']))
async def nft_item_offer_handler(message: Message):
    # Получаем коллекцию из текста сообщения
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply("❗️Please specify the collection slug after the /nft_item_offer command.")
        return

    user_id = message.from_user.id
    collection_slug = text[1].strip().lower()
    event_type = 'offer'  # Указываем тип события

    # Получаем язык пользователя из базы данных
    language = get_user_language(user_id)

    # Проверяем, существует ли уже подписка на этот тип события
    existing_subscription = get_active_subscription(user_id, collection_slug, event_type)
    if existing_subscription:
        await message.reply(f"❗️You are already subscribed to offer updates for the collection {collection_slug}.")
        return

    # Создаем новую подписку в БД с указанием типа события
    create_subscription(user_id, collection_slug, event_type)

    try:
        # Запуск TypeScript скрипта через Node.js
        process = subprocess.Popen(['node', 'app/bot/scripts/subscribe_item_offer.js', collection_slug, str(user_id)])
        print(f"Process started with PID: {process.pid}")
        await message.reply(f"✅ Subscription to offer updates in the {collection_slug} collection has been activated.")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply(f"❗️An error occurred while starting the subscription: {e}")






# Функция для обработки команды /nft_item_transferred
@dp.message(Command(commands=['nft_item_transferred']))
async def nft_item_transferred_handler(message: Message):
    # Получаем коллекцию из текста сообщения
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply("❗️Please specify the collection slug after the /nft_item_transferred command.")
        return

    user_id = message.from_user.id
    collection_slug = text[1].strip().lower()
    event_type = "item_transferred"

    # Получаем язык пользователя из базы данных
    language = get_user_language(user_id)

    # Проверяем, существует ли уже подписка
    existing_subscription = get_active_subscription(user_id, collection_slug, event_type)
    if existing_subscription:
        await message.reply(f"❗️You are already subscribed to transfer updates for the collection {collection_slug}.")
        return

    # Создаем новую подписку в БД
    create_subscription(user_id, collection_slug, event_type)

    try:
        # Запуск TypeScript скрипта через Node.js
        process = subprocess.Popen(['node', 'app/bot/scripts/subscribe_item_transferred.js', collection_slug, str(user_id)])
        print(f"Process started with PID: {process.pid}")
        await message.reply(f"✅ Subscription to item transfer events in the {collection_slug} collection has been activated.")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply(f"❗️An error occurred while starting the subscription: {e}")





# Обработчик команды /nft_item_cancelled
@dp.message(Command(commands=['nft_item_cancelled']))
async def nft_item_cancelled_handler(message: Message):
    # Получаем коллекцию из текста сообщения
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply("❗️Please specify the collection slug after the /nft_item_cancelled command.")
        return

    user_id = message.from_user.id
    collection_slug = text[1].strip().lower()

    # Получаем тип события
    event_type = 'cancelled'

    # Проверяем, существует ли уже подписка
    existing_subscription = get_active_subscription(user_id, collection_slug, event_type)
    if existing_subscription:
        await message.reply(f"❗️You are already subscribed to cancellation updates for the collection {collection_slug}.")
        return

    # Создаем новую подписку в БД
    create_subscription(user_id, collection_slug, event_type)

    try:
        # Запуск TypeScript скрипта через Node.js
        process = subprocess.Popen(['node', 'app/bot/scripts/subscribe_item_cancelled.js', collection_slug, str(user_id)])
        print(f"Process started with PID: {process.pid}")
        await message.reply(f"✅ Subscription to cancellation updates in the {collection_slug} collection has been activated.")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply(f"❗️An error occurred while starting the subscription: {e}")