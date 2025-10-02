# Crypto Risk Alert System

An AI-powered system for detecting and alerting on cryptocurrency risks including whale wallet transfers, smart contract vulnerabilities, and social sentiment analysis.

## Features

- **Whale Wallet Transfer Detection**: Monitor and alert on large cryptocurrency transfers
- **Smart Contract Scanner**: Analyze contracts for rug-pull risks and vulnerabilities
- **Social Sentiment Analysis**: Track sentiment across Twitter, Reddit, and other platforms
- **Explainable Risk Scores**: AI-driven risk assessment with detailed explanations
- **Multi-Channel Alerts**: Deliver alerts via Telegram, Discord, and web dashboard

## Architecture

### Core Components

1. **Blockchain Monitor** (`src/services/blockchain_monitor.py`)
   - Tracks whale wallet transfers
   - Monitors transaction patterns
   - Integrates with Etherscan, Web3 APIs

2. **Contract Scanner** (`src/services/contract_scanner.py`)
   - Analyzes smart contract code
   - Detects rug-pull patterns
   - Identifies security vulnerabilities

3. **Sentiment Analyzer** (`src/services/sentiment_analyzer.py`)
   - Scrapes social media platforms
   - Performs NLP sentiment analysis
   - Tracks trending topics and FUD

4. **Risk Scoring Engine** (`src/core/risk_engine.py`)
   - Aggregates data from all sources
   - Calculates weighted risk scores
   - Provides explainable AI insights

5. **Alert System** (`src/core/alert_manager.py`)
   - Manages alert delivery
   - Supports multiple channels
   - Handles alert priorities

### Alert Delivery

- **Telegram Bot** (`src/bots/telegram_bot.py`)
- **Discord Bot** (`src/bots/discord_bot.py`)
- **Web Dashboard** (`src/dashboard/`)

## Installation

```bash
# Clone the repository
git clone https://github.com/k2pitel/Crypto-Risk-Alert.git
cd Crypto-Risk-Alert

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/config.example.yml config/config.yml
# Edit config/config.yml with your API keys
```

## Configuration

Create a `config/config.yml` file with the following structure:

```yaml
blockchain:
  etherscan_api_key: "your_key_here"
  infura_project_id: "your_project_id"
  networks:
    - ethereum
    - bsc
    - polygon

sentiment:
  twitter_api_key: "your_key"
  twitter_api_secret: "your_secret"
  reddit_client_id: "your_client_id"
  reddit_client_secret: "your_secret"

alerts:
  telegram_bot_token: "your_bot_token"
  discord_bot_token: "your_bot_token"

risk_thresholds:
  whale_transfer_usd: 1000000
  contract_risk_score: 7.0
  sentiment_drop_threshold: -0.3
```

## Usage

### Start the System

```bash
# Start the main monitoring service
python src/main.py

# Start Telegram bot
python src/bots/telegram_bot.py

# Start Discord bot
python src/bots/discord_bot.py

# Start web dashboard
python src/dashboard/app.py
```

### API Endpoints

The system exposes a REST API for programmatic access:

- `GET /api/v1/risks/current` - Get current risk assessments
- `GET /api/v1/whales/transfers` - Recent whale transfers
- `GET /api/v1/contracts/{address}/scan` - Scan a contract
- `GET /api/v1/sentiment/{symbol}` - Get sentiment for a token
- `POST /api/v1/alerts/subscribe` - Subscribe to alerts

## Workflow

1. **Data Collection**
   - Blockchain monitor fetches on-chain data every 30 seconds
   - Sentiment analyzer scrapes social platforms every 5 minutes
   - Contract scanner runs on-demand and scheduled checks

2. **Risk Analysis**
   - Raw data is processed and normalized
   - ML models calculate risk scores
   - Explainability engine generates insights

3. **Alert Generation**
   - High-risk events trigger immediate alerts
   - Medium-risk events are batched hourly
   - Low-risk events appear only on dashboard

4. **Delivery**
   - Alerts are sent to subscribed channels
   - Dashboard updates in real-time
   - Historical data is stored for analysis

## Roadmap

### Phase 1: MVP (Months 1-2)
- [x] Core architecture design
- [x] Whale transfer detection
- [x] Basic contract scanner
- [x] Simple sentiment analysis
- [x] Telegram/Discord bots
- [x] Basic web dashboard

### Phase 2: Enhanced Analytics (Months 3-4)
- [ ] Advanced ML models for risk prediction
- [ ] Cross-chain support (Solana, Avalanche, etc.)
- [ ] Real-time contract execution monitoring
- [ ] Enhanced sentiment NLP with transformers
- [ ] Historical risk pattern analysis
- [ ] Custom alert rules

### Phase 3: Portfolio Risk Management (Months 5-6)
- [ ] Portfolio tracking integration
- [ ] Personal risk assessment
- [ ] Automated portfolio rebalancing suggestions
- [ ] DeFi protocol risk monitoring
- [ ] Yield farming risk analysis
- [ ] NFT collection risk scoring

### Phase 4: Enterprise Features (Months 7-9)
- [ ] White-label solutions
- [ ] Custom integrations
- [ ] Advanced API access
- [ ] Institutional-grade reporting
- [ ] Compliance monitoring
- [ ] Multi-tenant architecture

## Monetization Strategy

### Freemium Model
- **Free Tier**
  - 10 alerts per day
  - Basic risk scores
  - Community dashboard access
  - Single blockchain network

- **Pro Tier** ($29/month)
  - Unlimited alerts
  - Advanced risk analysis
  - All blockchain networks
  - Custom alert rules
  - API access (1000 requests/day)

- **Premium Tier** ($99/month)
  - Everything in Pro
  - Portfolio risk management
  - Real-time monitoring
  - Priority support
  - API access (10000 requests/day)
  - Historical data export

### Enterprise (Custom Pricing)
- White-label deployment
- Unlimited API access
- Custom integrations
- Dedicated support
- SLA guarantees
- On-premise deployment option

### API Access (Pay-as-you-go)
- $0.01 per risk assessment
- $0.05 per contract scan
- $0.001 per sentiment query
- Volume discounts available

## Technical Stack

- **Backend**: Python, FastAPI
- **ML/AI**: scikit-learn, transformers, PyTorch
- **Blockchain**: Web3.py, Etherscan API
- **Sentiment**: Tweepy, PRAW, BeautifulSoup
- **Database**: PostgreSQL, Redis
- **Task Queue**: Celery
- **Frontend**: React (dashboard)
- **Deployment**: Docker, Kubernetes

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_risk_engine.py
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - see LICENSE file for details

## Support

- Documentation: [https://docs.cryptoriskalert.io](https://docs.cryptoriskalert.io)
- Discord: [https://discord.gg/cryptoriskalert](https://discord.gg/cryptoriskalert)
- Email: support@cryptoriskalert.io