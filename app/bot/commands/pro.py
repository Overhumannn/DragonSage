from aiogram import types
from aiogram.filters import Command
from bot import dp
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя

# Команда для отображения информации о Pro-подписке
@dp.message(Command(commands=['pro']))
async def send_pro_info(message: types.Message):
    user_id = message.from_user.id
    # Получаем язык пользователя
    language = get_user_language(user_id)

    # Формируем сообщение о Pro-подписке на основе языка
    if language == 'ru':
        detailed_pro_message = (
            f"🌟 <b>Откройте весь потенциал с DragonSage Pro!</b> 🌟\n\n"
            f"С <b>Pro-подпиской</b> вы получите доступ к продвинутым инструментам на базе ИИ и эксклюзивным функциям для глубокого анализа рынка:\n\n"
            
            f"🔮 <b>Pro-функции на основе ИИ</b>:\n"
            f"• <b>/ainews</b> - Анализ новостей криптовалют с помощью ИИ: Получайте последние новости криптовалют, проанализированные ИИ для понимания рыночных трендов.\n"
            f"• <b>/aivoice</b> - Анализ голосовых сообщений: Отправляйте голосовые сообщения для получения инсайтов, основанных на ваших идеях.\n"
            f"• <b>/aita</b> - Индикаторы в реальном времени: Моментальный доступ к основным рыночным индикаторам, таким как RSI, MACD, полосы Боллинджера и другие.\n"
            f"• <b>/aistrat</b> - Торговые стратегии на базе ИИ: Генерируйте персонализированные стратегии торговли на основе данных и индикаторов в реальном времени.\n"
            f"• <b>/aibuysell</b> - Торговые сигналы на основе ИИ: Получайте сигналы для покупки/продажи в реальном времени на основе технических индикаторов и анализа ИИ.\n\n"
            
            f"🚀 <b>DEX TOPS Pro-команды</b>:\n"
            f"• <b>/dex_eth</b> - Отслеживайте топ-10 самых быстрорастущих токенов на Uniswap.\n"
            f"• <b>/dex_tron</b> - Следите за самыми быстрорастущими токенами на Tron DEX.\n\n"

            f"⛔️ <b>SCAM Pro-команды</b>:\n"
            f"• <b>/scam_limits</b> - Проверьте лимиты токенов, чтобы избежать подозрительных проектов.\n"
            f"• <b>/scam_fees</b> - Анализируйте комиссии газа, чтобы избежать скрытых затрат.\n"
            f"• <b>/scam_holder_analysis</b> - Проверка безопасности держателей токенов.\n"
            f"• <b>/scam_contract</b> - Анализ безопасности смарт-контрактов для предотвращения скрытых рисков.\n"
            f"• <b>/scam_simulate_trade</b> - Симулируйте продажу токенов, чтобы проверить проблемы с ликвидностью.\n\n"
        
            f"🐳 <b>WHALES Pro-команды</b>:\n"
            f"• <b>/whales</b> - Отслеживайте крупнейшие ордера на Binance в реальном времени.\n\n"

            f"💼 <b>LIVE-мониторинг NFT</b>:\n"
            f"• <b>/nft_item_listed</b> - Получайте уведомления, когда новые предметы добавляются на OpenSea.\n"
            f"• <b>/nft_item_offer</b> - Следите за предложениями, сделанными для NFT в вашей коллекции.\n"
            f"• <b>/nft_item_transferred</b> - Отслеживайте передачи предметов между владельцами NFT.\n"
            f"• <b>/nft_item_cancelled</b> - Получайте оповещения, когда листинги отменяются.\n\n"

            f"💸 <b>Готовы оформить подписку на Pro?</b>\n"
            f"Откройте все эти функции всего за <b>5 долларов в месяц</b>! Используйте сервис оплаты Cryptomus для отправки $5 в стейблкоинах, и ваша подписка будет активирована немедленно!\n\n"
            
            f"<b>Наслаждайтесь полной мощностью DragonSage Pro и будьте на шаг впереди в мире криптовалют и NFT!</b> 🚀"
        )
    else:
        detailed_pro_message = (
            f"🌟 <b>Unlock the full potential with DragonSage Pro!</b> 🌟\n\n"
            f"With the <b>Pro subscription</b>, you gain access to advanced tools powered by AI and exclusive features for in-depth market analysis:\n\n"
            
            f"🔮 <b>AI Pro Features</b>:\n"
            f"• <b>/ainews</b> - AI-Analyzed Crypto News: Get the latest crypto news analyzed by AI to help you understand market trends.\n"
            f"• <b>/aivoice</b> - Voice Message Analysis: Send voice messages for crypto-related insights based on your spoken ideas.\n"
            f"• <b>/aita</b> - Real-Time Technical Indicators: Instantly access key market indicators such as RSI, MACD, Bollinger Bands and more.\n"
            f"• <b>/aistrat</b> - AI-Powered Trading Strategies: Generate personalized trading strategies based on real-time data and indicators.\n"
            f"• <b>/aibuysell</b> - AI Trading Signals: Get real-time buy/sell signals based on technical indicators and AI analysis.\n\n"
            
            f"🚀 <b>DEX TOPS Pro Commands</b>:\n"
            f"• <b>/dex_eth</b> - Track the top 10 fastest-growing tokens on Uniswap.\n"
            f"• <b>/dex_tron</b> - Monitor the fastest-growing tokens on Tron DEX.\n\n"

            f"⛔️ <b>SCAM Pro Commands</b>:\n"
            f"• <b>/scam_limits</b> - Check token limits to avoid suspicious projects.\n"
            f"• <b>/scam_fees</b> - Analyze gas fees to avoid hidden costs.\n"
            f"• <b>/scam_holder_analysis</b> - Token holder safety checks.\n"
            f"• <b>/scam_contract</b> - Smart contract security analysis to avoid hidden risks.\n"
            f"• <b>/scam_simulate_trade</b> - Simulate token sales to check for liquidity issues.\n\n"
        
            f"🐳 <b>WHALES Pro Commands</b>:\n"
            f"• <b>/whales</b> - Track the largest orders on Binance in real-time.\n\n"

            f"💼 <b>NFT LIVE Monitoring</b>:\n"
            f"• <b>/nft_item_listed</b> - Get notified when new items are listed on OpenSea.\n"
            f"• <b>/nft_item_offer</b> - Stay updated on offers made for NFTs in your collection.\n"
            f"• <b>/nft_item_transferred</b> - Track item transfers between NFT holders.\n"
            f"• <b>/nft_item_cancelled</b> - Get alerts when listings are canceled.\n\n"

            f"💸 <b>Ready to subscribe to Pro?</b>\n"
            f"Unlock all of these features for only <b>$5 per month</b>! Use the Cryptomus payment service to send $5 in stablecoins, and your subscription will be activated immediately!\n\n"
            
            f"<b>Enjoy the full power of DragonSage Pro and stay ahead in the world of crypto and NFTs!</b> 🚀"
        )

    # Отправляем сообщение пользователю
    await message.reply(detailed_pro_message, parse_mode="HTML")
