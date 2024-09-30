from aiogram import types 
from aiogram.filters import Command
from bot import dp
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя

# Welcome message with detailed information
@dp.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    
    # Получаем язык пользователя
    language = get_user_language(user_id)
    
    # Формируем информативное сообщение с примерами команд на основе языка
    if language == 'ru':
        detailed_start_message = (
            f"👋 <b>Добро пожаловать в DragonSageBot</b>! 🐉\n\n"
            f"🌟 <b>DragonSageBot</b> — это мощный инструмент для криптоэнтузиастов, трейдеров и коллекционеров NFT. "
            f"Используя наши уникальные команды, этот бот поможет вам с техническим анализом, ценами криптовалют, мониторингом NFT и многим другим!\n\n"
            f"Вот некоторые основные функции и команды, которые вы можете попробовать:\n\n"
            f"⚙️ <b>Основные команды</b>:\n"
            f"• <b>/price</b> [symbol] — Получите последнюю цену любой криптовалюты. Пример: <b>/price BTC</b>\n"
            f"• <b>/best</b> — Просмотр списка лидеров по росту за последние 24 часа.\n"
            f"• <b>/worst</b> — Узнайте, какие криптовалюты потеряли наибольшую ценность за последние 24 часа.\n"
            f"• <b>/ath</b> [symbol] — Найдите исторический максимум (ATH) цены любой криптовалюты. Пример: <b>/ath ETH</b>\n"
            f"• <b>/ta</b> — Предоставляет технический анализ криптовалюты с использованием индикаторов и данных биржи Binance. Пример: <b>/ta ETH</b>\n\n"
                
            f"📊 <b>Анализ рынка</b>:\n"
            f"• <b>/charts</b> [symbol] — Просмотрите графики цен за последний год для любой криптовалюты. Пример: <b>/charts BTC</b>\n"
            f"• <b>/compare</b> [symbol1] [symbol2] — Сравните две криптовалюты. Пример: <b>/compare BTC ETH</b>\n"
            f"• <b>/convert</b> [symbol1] [symbol2] — Мгновенно конвертируйте одну криптовалюту в другую по ценам Binance. Пример: <b>/convert BTC USDT</b>\n\n"
                
            f"⛑ <b>SCAM команды</b>:\n"
            f"• <b>/scam_token</b> [адрес токена] — Позволяет пользователям проверить токен на мошенничество. Пример: <b>/scam_token 0x1234abcd...</b>\n"
            f"• <b>/scam_liquidity</b> [адрес токена] — Быстро проверьте ликвидность токена на децентрализованных биржах (DEX). Пример: <b>/scam_liquidity 0x1234abcd...</b>\n"
            f"• <b>/scam_flags</b> [адрес токена] — Помогает пользователям определить потенциально мошеннические токены, отображая предупреждения. Пример: <b>/scam_flags 0x1234abcd...</b>\n\n"
                
            f"🏞 <b>NFT функции</b>:\n"
            f"• <b>/nft</b> [коллекция] — Получите подробную статистику по любой коллекции NFT на OpenSea. Пример: <b>/nft cryptopunks</b>\n"
            f"• <b>/nft_events</b> [коллекция] — Отслеживайте последние события для коллекции NFT. Пример: <b>/nft_events cryptopunks</b>\n\n"
                
            f"🛠 <b>Технические инструменты</b>:\n"
            f"• <b>/gas_fees</b> — Узнайте текущие комиссии за газ для сетей Ethereum и BSC.\n"
            f"• <b>/google</b> [ключевое слово] — Анализируйте популярность ключевых слов с помощью Google Trends. Пример: <b>/google Bitcoin</b>\n"
            f"• <b>/heatmap</b> — Визуализируйте рынок криптовалют с помощью тепловой карты.\n\n"
                
            f"✨ <b>PRO функции</b>:\n"
            f"• <b>/ainews</b> — Получите анализ последних новостей криптовалют с помощью AI.\n"
            f"• <b>/aivoice</b> — Отправьте голосовые сообщения для AI-анализа в контексте криптовалют.\n"
            f"• <b>/aistrat</b> — Инновационный инструмент, анализирующий рынок с помощью технических индикаторов и AI.\n"
            f"• <b>/aibuysell</b> — Получите торговые сигналы на основе технических индикаторов криптовалют с использованием искусственного интеллекта.\n"
            f"• <b>И МНОГИЕ ДРУГИЕ ПОЛЕЗНЫЕ КОМАНДЫ!</b>\n"
            f"• <b>/pro</b> — Узнайте о подписке Pro для доступа к эксклюзивным функциям.\n\n"
                
            f"🔔 <b>Будьте в курсе событий</b>:\n"
            f"Включите уведомления о событиях или коллекциях с помощью команд <b>/nft_item_listed</b>, <b>/nft_item_offer</b> или <b>/nft_item_cancelled</b>.\n\n"
                
            f"⚡️ <b>Нужна помощь?</b>\n"
            f"Используйте <b>/help</b> в любое время, чтобы увидеть список команд с объяснениями и примерами!\n\n"

            f"⚡️ <b>Хотите оформить pro-подписку?</b>\n"
            f"Используйте <b>/pro</b> в любое время, чтобы увидеть список pro команд и узнать как её оформить!\n\n"

            f"<b>Добро пожаловать на борт! Давайте вместе погрузимся в мир криптовалют! 🚀🚀🚀</b>"
        )
    else:
        detailed_start_message = (
            f"👋 <b>Welcome to DragonSageBot</b>! 🐉\n\n"
            f"🌟 <b>DragonSageBot</b> is a powerful tool for crypto enthusiasts, traders, and NFT collectors. "
            f"Using our unique commands, this bot helps you with technical analysis, crypto prices, NFT monitoring, and much more!\n\n"
            f"Here are some of the main features and commands you can try out:\n\n"
            f"⚙️ <b>Core Commands</b>:\n"
            f"• <b>/price</b> [symbol] - Get the latest price of any cryptocurrency. Example: <b>/price BTC</b>\n"
            f"• <b>/best</b> - View the list of top gainers in the last 24 hours.\n"
            f"• <b>/worst</b> - Check which cryptocurrencies lost the most value over the last 24 hours.\n"
            f"• <b>/ath</b> [symbol] - Find the all-time high (ATH) price of any cryptocurrency. Example: <b>/ath ETH</b>\n"
            f"• <b>/ta</b> - Provides technical analysis of cryptocurrency using indicators and data from the Binance exchange. Example: <b>/ta ETH</b>\n\n"
            
            f"📊 <b>Market Analysis</b>:\n"
            f"• <b>/charts</b> [symbol] - View price charts for the last year for any crypto. Example: <b>/charts BTC</b>\n"
            f"• <b>/compare</b> [symbol1] [symbol2] - Compare two cryptocurrencies. Example: <b>/compare BTC ETH</b>\n"
            f"• <b>/convert</b> [symbol1] [symbol2] - Instantly convert one cryptocurrency to another based on Binance prices. Example: <b>/convert BTC USDT</b>\n\n"
            
            f"⛑ <b>SCAM commands</b>:\n"
            f"• <b>/scam_token</b> [token_address] - Allows users to check a token for fraudulent activity. Example: <b>/scam_token 0x1234abcd...</b>\n"
            f"• <b>/scam_liquidity</b> [token_address] - Allows users to quickly check the liquidity of a token on decentralized exchanges (DEX). Example: <b>/scam_liquidity 0x1234abcd...</b>\n"
            f"• <b>/scam_flags</b> [token_address] - Helps users identify potentially fraudulent tokens by displaying warning flags related to token security. Example: <b>/scam_flags 0x1234abcd...</b>\n\n"
            
            f"🏞 <b>NFT Features</b>:\n"
            f"• <b>/nft</b> [collection] - Get detailed stats for any NFT collection on OpenSea. Example: <b>/nft cryptopunks</b>\n"
            f"• <b>/nft_events</b> [collection] - Track the latest events for an NFT collection. Example: <b>/nft_events cryptopunks</b>\n\n"
            
            f"🛠 <b>Technical Tools</b>:\n"
            f"• <b>/gas_fees</b> - Check the current gas fees for Ethereum and BSC networks.\n"
            f"• <b>/google</b> [keyword] - Analyze the popularity of keywords using Google Trends. Example: <b>/google Bitcoin</b>\n"
            f"• <b>/heatmap</b> - Visualize the crypto market with a heatmap.\n\n"
            
            f"✨ <b>PRO Features</b>:\n"
            f"• <b>/ainews</b> - Get AI-powered analysis of the latest crypto news.\n"
            f"• <b>/aivoice</b> - Send voice messages for AI analysis in the crypto context.\n"
            f"• <b>/aistrat</b> - An innovative tool that analyzes the market using technical indicators and AI.\n"
            f"• <b>/aibuysell</b> - Allows users to receive trading signals based on technical indicators of cryptocurrencies using artificial intelligence.\n"
            f"• <b>AND MANY OTHER COOL COMMANDS!</b>\n"
            f"• <b>/pro</b> - Learn about the Pro subscription to access exclusive features.\n\n"

            f"🔔 <b>Stay Up-to-Date</b>:\n"
            f"Enable notifications for specific events or collections using commands like <b>/nft_item_listed</b>, <b>/nft_item_offer</b>, or <b>/nft_item_cancelled</b>.\n\n"
            
            f"⚡️ <b>Need Help?</b>\n"
            f"Use <b>/help</b> at any time to see a list of available commands and get assistance!\n\n"

            f"⚡️ <b>Want to get a pro subscription?</b>\n"
            f"Use <b>/pro</b> at any time to see a list of pro commands and learn how to get one!\n\n"
            
            f"<b>Welcome aboard! Let’s dive into the world of crypto together! 🚀🚀🚀</b>"
        )

    # Отправляем ответное сообщение пользователю
    await message.reply(detailed_start_message, parse_mode="HTML")
