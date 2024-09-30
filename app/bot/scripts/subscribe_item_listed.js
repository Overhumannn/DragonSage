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

// Подписка на событие "Item Listed"
client.onItemListed(collectionSlug, (event) => {
    console.log(`Новый предмет выставлен на продажу в коллекции ${collectionSlug} для пользователя ${telegramId}`);
    // Здесь можно добавить код для отправки уведомления пользователю через HTTP-запрос к серверу, который отправит сообщение пользователю в Telegram
});

// Подключение к WebSocket
client.connect();
