from aiogram import types
from aiogram.filters import Command
from bot import dp
from app.database.crud import get_user_language  # Импорт функции для получения языка пользователя

# Команда для отображения информации о популярных и сложных командах
@dp.message(Command(commands=['help']))
async def send_help(message: types.Message):
    user_id = message.from_user.id
    # Получаем язык пользователя
    language = get_user_language(user_id)

    # Формируем сообщение на основе языка пользователя
    if language == 'ru':
        detailed_help_message = (
            f"🛠 <b>Помощь DragonSageBot</b> 🛠\n\n"
            f"Здесь вы найдете объяснения для самых популярных и сложных команд, доступных в DragonSageBot.\n\n"
            
            f"🔍 <b>Популярные команды</b>:\n"
            f"• <b>/price</b> [symbol] - Эта команда получает текущую цену любой криптовалюты. Просто введите символ интересующей вас криптовалюты. Пример: <b>/price BTC</b> покажет текущую цену биткойна.\n\n"
            
            f"• <b>/best</b> - Хотите узнать, какие криптовалюты выросли больше всего за последние 24 часа? Используйте эту команду, чтобы увидеть лидеров рынка.\n\n"
            
            f"• <b>/worst</b> - Если вы отслеживаете падение рынка, эта команда покажет вам криптовалюты, которые потеряли больше всего в стоимости за последние 24 часа.\n\n"
            
            f"• <b>/ath</b> [symbol] - Хотите узнать исторический максимум цены криптовалюты? Эта команда покажет вам самую высокую зарегистрированную цену. Пример: <b>/ath ETH</b>.\n\n"
            
            f"• <b>/ta</b> [symbol] - Эта команда предоставляет технический анализ на основе рыночных индикаторов, таких как RSI, MACD и полосы Боллинджера. Используйте <b>/ta</b> с символом криптовалюты, чтобы увидеть данные. Пример: <b>/ta ETH</b> для эфира.\n\n"
            
            f"📊 <b>Продвинутые рыночные команды</b>:\n"
            f"• <b>/charts</b> [symbol] - Хотите увидеть тренд цены криптовалюты? Используйте <b>/charts BTC</b>, чтобы сгенерировать график цен за последний год и визуализировать рыночные тренды.\n\n"
            
            f"• <b>/compare</b> [symbol1] [symbol2] - Эта команда позволяет сравнивать две криптовалюты. Например, <b>/compare BTC ETH</b> сравнит биткойн и эфир на основе ключевых рыночных индикаторов.\n\n"
            
            f"• <b>/convert</b> [symbol1] [symbol2] - Мгновенно конвертируйте одну криптовалюту в другую. Пример: <b>/convert BTC USDT</b> покажет, сколько стоит 1 биткойн в USDT.\n\n"
            
            f"⚠️ <b>Команды для обнаружения мошенничества</b>:\n"
            f"• <b>/scam_token</b> [адрес токена] - Используйте эту команду, чтобы проверить, есть ли признаки мошенничества у токена. Просто укажите адрес контракта токена. Пример: <b>/scam_token 0x1234abcd...</b>\n\n"
            
            f"• <b>/scam_liquidity</b> [адрес токена] - Опасаетесь за ликвидность? Эта команда проверяет ликвидность токена на децентрализованных биржах, помогая вам оценить его торгуемость. Пример: <b>/scam_liquidity 0x1234abcd...</b>\n\n"
            
            f"• <b>/scam_flags</b> [адрес токена] - Если вы сомневаетесь в безопасности токена, используйте эту команду, чтобы выявить подозрительные признаки активности токена. Пример: <b>/scam_flags 0x1234abcd...</b>\n\n"
            
            f"⚡️ <b>Команды на базе ИИ</b>:\n"
            f"• <b>/ainews</b> - Получите анализ новостей криптовалют в реальном времени на основе ИИ. Эта команда сканирует мировые источники новостей и предоставляет инсайты о том, как они могут повлиять на рынок.\n\n"
            
            f"• <b>/aivoice</b> - Хотите анализировать свои мысли о криптовалюте на ходу? Отправьте голосовое сообщение с помощью <b>/aivoice</b>, и бот транскрибирует и проанализирует его, предоставив вам полезные инсайты.\n\n"
            
            f"• <b>/aistrat</b> [symbol] - Нужна стратегия? Эта команда генерирует персонализированные торговые стратегии на основе ИИ и текущих рыночных условий. Просто введите, например: <b>/aistrat BTC</b>, и ИИ все сделает за вас!\n\n"
            
            f"• <b>/aibuysell</b> [symbol] - Получите мгновенные сигналы для покупки/продажи на основе технических индикаторов, таких как RSI, MACD и других. Пример: <b>/aibuysell BTC</b> для сигналов по биткойну.\n\n"
            
            f"💼 <b>Мониторинг NFT</b>:\n"
            f"• <b>/nft_item_listed</b> [коллекция] - Получайте мгновенные уведомления, когда новые предметы добавляются в вашу любимую коллекцию NFT на OpenSea. Пример: <b>/nft_item_listed cryptopunks</b>\n\n"
            
            f"• <b>/nft_item_offer</b> [коллекция] - Оставайтесь в курсе предложений, сделанных для ваших предметов NFT с помощью этой команды. Пример: <b>/nft_item_offer cryptopunks</b>\n\n"
            
            f"• <b>/nft_item_transferred</b> [коллекция] - Отслеживайте передачи предметов в коллекциях NFT. Пример: <b>/nft_item_transferred cryptopunks</b>\n\n"
            
            f"⚙️ <b>Другие полезные инструменты</b>:\n"
            f"• <b>/gas_fees</b> - Узнайте текущие комиссии за газ в сетях Ethereum и BSC.\n\n"
            
            f"• <b>/google</b> [ключевое слово] - Анализируйте популярность ключевых слов с помощью Google Trends. Пример: <b>/google Bitcoin</b>\n\n"
            
            f"• <b>/heatmap</b> - Визуализируйте рынок криптовалют с помощью тепловой карты, чтобы получить обзор текущих тенденций.\n\n"
            
            f"• <b>/whales</b> - Позволяет пользователям отслеживать крупнейшие ордера на криптовалютной бирже Binance за последнее время. Пример: <b>/whales BTCUSDT</b>\n\n"
    
                f"💡 <b>Нужна дополнительная помощь?</b>\n"
            f"Не стесняйтесь спрашивать! Введите <b>/start</b> или <b>/help</b> снова, чтобы просмотреть команды или получить помощь в любое время. Давайте сделаем ваше криптопутешествие легче! 🚀"
        )
    else:
        detailed_help_message = (
            f"🛠 <b>DragonSageBot Help</b> 🛠\n\n"
            f"Here you can find explanations for the most popular and complex commands available in DragonSageBot.\n\n"
            
            f"🔍 <b>Popular Commands</b>:\n"
            f"• <b>/price</b> [symbol] - This command fetches the real-time price of any cryptocurrency. Simply enter the symbol of the cryptocurrency you're interested in. Example: <b>/price BTC</b> will show you the latest Bitcoin price.\n\n"
            
            f"• <b>/best</b> - Want to know which cryptocurrencies have grown the most in the last 24 hours? Use this command to see the top gainers in the market.\n\n"
            
            f"• <b>/worst</b> - If you're tracking market downturns, this command will show you the cryptocurrencies that lost the most value in the last 24 hours.\n\n"
            
            f"• <b>/ath</b> [symbol] - Curious about the all-time high price of a specific cryptocurrency? This command shows the highest price ever recorded. Example: <b>/ath ETH</b>.\n\n"

            f"• <b>/ta</b> [symbol] - This command provides technical analysis based on market indicators such as RSI, MACD, and Bollinger Bands. Use <b>/ta</b> followed by the cryptocurrency symbol to see the data. Example: <b>/ta ETH</b> for Ethereum.\n\n"
            
            f"📊 <b>Advanced Market Commands</b>:\n"
            f"• <b>/charts</b> [symbol] - Want to see the price trend of a cryptocurrency? Use <b>/charts BTC</b> to generate a price chart for the last year, helping you visualize market trends.\n\n"
            
            f"• <b>/compare</b> [symbol1] [symbol2] - This command allows you to compare two cryptocurrencies side by side. For instance, <b>/compare BTC ETH</b> will compare Bitcoin and Ethereum based on key market indicators.\n\n"
            
            f"• <b>/convert</b> [symbol1] [symbol2] - Instantly convert one cryptocurrency to another. Example: <b>/convert BTC USDT</b> will show you how much 1 Bitcoin is worth in USDT.\n\n"
            
            f"⚠️ <b>SCAM Detection Commands</b>:\n"
            f"• <b>/scam_token</b> [token_address] - Use this command to check whether a token has signs of being fraudulent. Simply provide the token’s contract address. Example: <b>/scam_token 0x1234abcd...</b>\n\n"
            
            f"• <b>/scam_liquidity</b> [token_address] - Concerned about liquidity? This command checks the liquidity of a token on decentralized exchanges, helping you assess its tradability. Example: <b>/scam_liquidity 0x1234abcd...</b>\n\n"
            
            f"• <b>/scam_flags</b> [token_address] - If you're unsure about a token's safety, use this command to identify red flags like suspicious token activity. Example: <b>/scam_flags 0x1234abcd...</b>\n\n"
            
            f"⚡️ <b>AI-Powered Commands</b>:\n"
            f"• <b>/ainews</b> - Get real-time AI-driven analysis of the latest cryptocurrency news. This command scans global news sources and provides insights on how they might affect the market.\n\n"
            
            f"• <b>/aivoice</b> - Want to analyze your crypto thoughts on the go? Send a voice message using <b>/aivoice</b>, and the bot will transcribe and analyze it to give you valuable insights.\n\n"
            
            f"• <b>/aistrat</b> [symbol] - Need a strategy? This command generates personalized trading strategies using AI based on real-time market conditions. Just enter, for example: <b>/aistrat BTC</b>, and let AI do the work!\n\n"
            
            f"• <b>/aibuysell</b> [symbol] - Receive instant buy/sell signals based on technical indicators such as RSI, MACD, and more. Example: <b>/aibuysell BTC</b> for Bitcoin signals.\n\n"
            
            f"💼 <b>NFT Monitoring</b>:\n"
            f"• <b>/nft_item_listed</b> [collection] - Get instant notifications when new items are listed in your favorite NFT collections on OpenSea. Example: <b>/nft_item_listed cryptopunks</b>\n\n"
            
            f"• <b>/nft_item_offer</b> [collection] - Stay up to date on offers made on your NFT items with this command. Example: <b>/nft_item_offer cryptopunks</b>\n\n"
            
            f"• <b>/nft_item_transferred</b> [collection] - Track item transfers in NFT collections. Example: <b>/nft_item_transferred cryptopunks</b>\n\n"
            
            f"⚙️ <b>Other Useful Tools</b>:\n"
            f"• <b>/gas_fees</b> - Check the current gas fees for Ethereum and BSC networks.\n\n"
            
            f"• <b>/google</b> [keyword] - Analyze the popularity of keywords through Google Trends. Example: <b>/google Bitcoin</b>\n\n"
            
            f"• <b>/heatmap</b> - Visualize the crypto market with a heatmap to get a bird’s-eye view of the current trends.\n\n"

            f"• <b>/whales</b> - Allows users to track the largest orders on the Binance cryptocurrency exchange in recent times. Example: <b>/whales BTCUSDT</b>\n\n"
    
            f"💡 <b>Need more assistance?</b>\n"
            f"Don't hesitate to ask! Type <b>/start</b> or <b>/pro</b> to review commands or get help anytime. Let's make your crypto journey smoother! 🚀"
        )

    # Отправляем сообщение пользователю
    await message.reply(detailed_help_message, parse_mode="HTML")
