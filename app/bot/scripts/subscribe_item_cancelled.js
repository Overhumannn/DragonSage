import { OpenSeaStreamClient } from '@opensea/stream-js';
import { WebSocket } from 'ws';
import { LocalStorage } from 'node-localstorage';
import axios from 'axios';

// Получаем аргументы командной строки
const [,, collectionSlug, telegramId] = process.argv;

// Инициализация клиента OpenSea
const client = new OpenSeaStreamClient({
    token: process.env.OPENSEA_API_KEY,
    connectOptions: {
        transport: WebSocket,
        sessionStorage: LocalStorage
    }
});

// Хранение последних обработанных событий
let lastProcessedEventId = null;

// Подписка на событие "Item Cancelled"
client.onItemCancelled(collectionSlug, async (event) => {
    // Проверяем, не обрабатывалось ли это событие ранее
    if (event.id === lastProcessedEventId) {
        console.log("Duplicate event ignored.");
        return;
    }

    // Обновляем последний обработанный идентификатор события
    lastProcessedEventId = event.id;

    console.log(`Order cancelled in collection ${collectionSlug} for user ${telegramId}`);

    // Отправляем уведомление пользователю через ваш бот
    try {
        await axios.post(`https://api.telegram.org/bot${process.env.BOT_TOKEN}/sendMessage`, {
            chat_id: telegramId,
            text: `❗️ Order cancelled in collection ${collectionSlug}`
        });
    } catch (error) {
        console.error('Error sending message to Telegram:', error);
    }
});

// Подключение к WebSocket
client.connect();