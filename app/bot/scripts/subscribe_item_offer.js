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

// Подписка на событие "Item Offer"
client.onItemReceivedOffer(collectionSlug, (event) => {
    console.log(`Получено предложение на предмет в коллекции ${collectionSlug} для пользователя ${telegramId}`);
    // Здесь можно добавить логику для отправки уведомления пользователю
    // Например, через HTTP-запрос на сервер, который отправит сообщение в Telegram
});

// Подключение к WebSocket
client.connect();
