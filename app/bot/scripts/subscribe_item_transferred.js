import { OpenSeaStreamClient } from '@opensea/stream-js';
import { WebSocket } from 'ws';
import { LocalStorage } from 'node-localstorage';

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

// Подписка на событие "Item Transferred"
client.onItemTransferred(collectionSlug, (event) => {
    console.log(`Предмет был передан в коллекции ${collectionSlug} для пользователя ${telegramId}`);
    // Здесь можно добавить код для отправки уведомления пользователю через Telegram
    // Например, сделать HTTP-запрос на сервер для отправки уведомления через API Telegram
});

// Подключение к WebSocket
client.connect();
