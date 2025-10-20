# DragonSage Bot

DragonSage is a comprehensive cryptocurrency and NFT analytics Telegram bot that provides real-time market data, technical analysis, and advanced trading insights. The bot offers both basic and premium features for cryptocurrency enthusiasts, traders, and NFT collectors.

## Features

### Basic Commands

#### 🚀 Getting Started
- `/start` - Initialize the bot and receive a personalized welcome message
- `/language` - Switch between Russian and English interface

#### 💰 Cryptocurrency Data
- `/price [symbol]` - Get real-time cryptocurrency prices with detailed market data
- `/ath [symbol]` - View all-time high prices with historical data from Binance
- `/best` - Display top 5 cryptocurrencies with highest 24h growth
- `/worst` - Show top 5 cryptocurrencies with biggest 24h losses
- `/compare [symbols]` - Compare multiple cryptocurrencies side-by-side
- `/convert [from] [to] [amount]` - Convert between cryptocurrencies using Binance rates
- `/description [symbol]` - Get comprehensive cryptocurrency information and official websites

#### 📊 Market Analysis
- `/charts [symbol]` - Generate detailed price charts powered by TradingView
- `/index` - View top 10 cryptocurrencies by market capitalization
- `/market_summary` - Get complete market overview with trading volumes and trends
- `/dex [symbol]` - Check cryptocurrency prices on decentralized exchanges
- `/sentiment` - View Fear & Greed Index with market sentiment analysis

#### ⛽ Network Information
- `/gas_fees` - Check current gas fees for Ethereum and Binance Smart Chain
- `/events` - Browse upcoming cryptocurrency events and announcements

#### 📈 Technical Analysis
- `/ta [symbol]` - Comprehensive technical analysis with indicators (RSI, MACD, SMA, etc.)
- `/google [keyword]` - Google Trends analysis for cryptocurrency-related searches

#### 🎨 NFT Analytics
- `/nft [collection]` - Detailed NFT collection statistics from OpenSea
- `/nft_events` - Latest NFT marketplace events and transactions
- `/nft_events_collection [collection]` - Collection-specific NFT events
- `/nft_events_account [address]` - Account-specific NFT activity
- `/nft_get_contract [blockchain] [address]` - Smart contract information
- `/nft_get_nft [blockchain] [contract] [token_id]` - Individual NFT details
- `/nft_listings_collection [collection]` - Active listings for NFT collections
- `/nft_offers_collection [collection]` - Current offers on NFT collections

#### 🛡️ Security Tools
- `/scam_token [address]` - Check if a token is potentially fraudulent
- `/scam_liquidity [address]` - Verify token liquidity on DEX platforms
- `/scam_flags [address]` - View security warnings and risk flags for tokens

### Premium (PRO) Commands

#### 🤖 AI-Powered Analysis
- `/ainews` - AI-generated analysis of latest cryptocurrency news with market impact assessment
- `/aivoice` - Voice message analysis with cryptocurrency context using GPT
- `/aita [symbol]` - AI-enhanced technical analysis with intelligent insights
- `/aistrat` - Personalized AI trading strategy recommendations
- `/aibuysell [symbol]` - AI-generated buy/sell signals based on technical indicators

#### 📊 Advanced DEX Analytics
- `/dex_eth` - Top 10 fastest-growing Ethereum tokens on Uniswap
- `/dex_tron` - Top 10 fastest-growing Tron DEX tokens
- `/cex_eth` - Fastest-growing Ethereum tokens on centralized exchanges
- `/cex_sol` - Fastest-growing Solana tokens on centralized exchanges  
- `/cex_ton` - Fastest-growing TON blockchain tokens on centralized exchanges

#### 🔍 Advanced Security Analysis
- `/scam_limits [address]` - Check buy/sell limits on tokens
- `/scam_fees [address]` - Analyze gas fees for potential scam indicators
- `/scam_holder_analysis [address]` - Analyze token holder selling capabilities
- `/scam_contract [address]` - Smart contract security analysis
- `/scam_simulate_trade [address]` - Simulate token trades to check liquidity

#### 🐋 Whale Tracking
- `/whales [pair]` - Monitor large orders and whale activity on Binance

#### 🔔 NFT Notifications
- `/nft_item_listed [collection]` - Subscribe to new NFT listings notifications
- `/nft_item_offer [collection]` - Subscribe to new offer notifications
- `/nft_item_transferred [collection]` - Subscribe to NFT transfer notifications
- `/nft_item_cancelled [collection]` - Subscribe to cancelled listing notifications

## Supported Platforms

- **Cryptocurrency Exchanges**: Binance, Bitget
- **DEX Platforms**: Uniswap, Tron DEX, PancakeSwap
- **NFT Platforms**: OpenSea
- **Data Sources**: CryptoCompare, TradingView, Google Trends
- **Blockchains**: Ethereum, Binance Smart Chain, Solana, TON, Tron, Polygon

## Key Features

### Real-Time Data
All market data is updated in real-time, ensuring users receive the most current information for their trading and investment decisions.

### Multi-Language Support
Full support for both English and Russian languages with automatic detection and adaptation.

### Comprehensive Analytics
From basic price queries to advanced technical analysis, the bot provides tools for users of all experience levels.

### Security Focus
Multiple commands dedicated to identifying potentially fraudulent tokens and protecting users from scams.

### AI Integration
Premium features powered by GPT for intelligent market analysis, news interpretation, and trading insights.

### NFT Market Coverage
Extensive NFT marketplace integration with real-time events, statistics, and notification systems.

## Technical Specifications

- **Platform**: Telegram Bot API
- **Programming Language**: Python
- **Data Sources**: Multiple cryptocurrency APIs and blockchain data providers
- **Real-time Updates**: WebSocket connections for live data
- **AI Processing**: GPT integration for advanced analysis
- **Database**: User preferences and subscription management

## Important Disclaimers

⚠️ **Investment Warning**: All trading signals, analysis, and recommendations provided by this bot are for informational purposes only and do not constitute professional financial advice. Users should conduct their own research and consult with financial advisors before making investment decisions.

🔒 **Security Notice**: Always verify token contracts and perform due diligence before trading. The security analysis tools are supplementary and should not be the sole basis for investment decisions.

## Bot Architecture

The bot is built with modularity in mind, featuring:
- Separate command handlers for different functionality areas
- Real-time data processing pipelines
- User session management
- Multi-language localization system
- Premium subscription management
- Notification and webhook systems for NFT events

## Data Accuracy

All data is sourced from reputable providers including major cryptocurrency exchanges and blockchain explorers. However, users should be aware that:
- Market data can be volatile and change rapidly
- Different exchanges may show slight price variations
- Historical data accuracy depends on source reliability
- AI analysis is based on available data patterns and should be used as supplementary information

## Usage Examples

### Basic Price Check
```
/price BTC
```
Returns comprehensive Bitcoin market data including current price, 24h change, volume, and market cap.

### Technical Analysis
```
/ta ETHUSDT
```
Provides detailed technical indicators for Ethereum including RSI, MACD, moving averages, and trend analysis.

### NFT Collection Analysis
```
/nft boredapeyachtclub
```
Returns detailed statistics for the Bored Ape Yacht Club collection including floor price, volume, and recent activity.

### Security Analysis
```
/scam_token 0x1234567890abcdef...
```
Analyzes the specified token address for potential security risks and scam indicators.

This bot represents a comprehensive solution for cryptocurrency and NFT market analysis, combining traditional financial indicators with modern AI capabilities to provide users with actionable market insights.
