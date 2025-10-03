# Quick Start Guide

Get the Crypto Risk Alert system running in under 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Git installed
- API keys (optional for testing)

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/k2pitel/Crypto-Risk-Alert.git
cd Crypto-Risk-Alert

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configure

```bash
# Copy example config
cp config/config.example.yml config/config.yml

# Edit with your API keys (optional for demo)
nano config/config.yml
```

### 3. Run the System

#### Option A: Run Everything with Docker

```bash
docker-compose up -d
```

#### Option B: Run Individually

```bash
# Activate virtual environment
source venv/bin/activate

# Start API Server
python src/api/app.py

# In another terminal: Start Main System
python src/main.py

# In another terminal: Start Telegram Bot
python src/bots/telegram_bot.py

# In another terminal: Start Discord Bot
python src/bots/discord_bot.py
```

## Testing the System

### 1. Check API Health

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "risk_engine": true,
    "blockchain_monitor": true,
    "contract_scanner": true,
    "sentiment_analyzer": true,
    "alert_manager": true
  }
}
```

### 2. Get Risk Assessment

```bash
curl http://localhost:8000/api/v1/risks/BTC
```

### 3. Scan a Contract

```bash
curl "http://localhost:8000/api/v1/contracts/0xdac17f958d2ee523a2206206994597c13d831ec7/scan?network=ethereum"
```

### 4. Get Whale Transfers

```bash
curl "http://localhost:8000/api/v1/whales/transfers?network=ethereum&hours_back=24"
```

## Using the Bots

### Telegram Bot

1. Find your bot on Telegram (use token to get bot username)
2. Start a chat: `/start`
3. Subscribe: `/subscribe`
4. Watch an asset: `/watch BTC`
5. Get risk assessment: `/risk BTC`

### Discord Bot

1. Invite bot to your server
2. In any channel: `!start`
3. Subscribe: `!subscribe`
4. Watch an asset: `!watch ETH`
5. Get risk: `!risk ETH`

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_risk_engine.py -v
```

## Demo Mode

Run without API keys for demonstration:

```bash
# The system will use mock data
python src/main.py
```

## Viewing Logs

```bash
# API logs
tail -f logs/crypto_risk_alert.log

# Docker logs
docker-compose logs -f
```

## Next Steps

1. **Configure API Keys**: Add your real API keys to `config/config.yml`
2. **Customize Alerts**: Adjust risk thresholds in config
3. **Add Watchers**: Subscribe to specific assets
4. **Deploy**: Follow `docs/DEPLOYMENT.md` for production setup

## Common Issues

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Errors

- Check that API keys are properly set in `config/config.yml`
- Ensure no extra spaces or quotes in the config file
- For demo mode, the system works with mock data

## Architecture Overview

```
User → Telegram/Discord Bot → Alert Manager → Risk Engine
                                    ↓
                         Blockchain Monitor
                         Contract Scanner
                         Sentiment Analyzer
                                    ↓
                              Data Sources
```

## Key Features Demonstrated

✅ **Whale Transfer Detection**
- Monitors large wallet movements
- Identifies exchange dumps
- Calculates transfer-based risk

✅ **Smart Contract Analysis**
- Detects rug-pull patterns
- Identifies honeypots
- Checks liquidity locks

✅ **Sentiment Analysis**
- Tracks Twitter/Reddit sentiment
- Identifies trending topics
- Calculates sentiment risk

✅ **Risk Scoring**
- Weighted risk calculation
- Explainable AI insights
- Actionable recommendations

✅ **Multi-Channel Alerts**
- Telegram notifications
- Discord embeds
- API webhooks (coming soon)

## API Endpoints Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/risks/{symbol}` | GET | Risk assessment |
| `/api/v1/whales/transfers` | GET | Whale transfers |
| `/api/v1/contracts/{address}/scan` | GET | Contract scan |
| `/api/v1/sentiment/{symbol}` | GET | Sentiment data |
| `/api/v1/alerts/subscribe` | POST | Subscribe to alerts |

Full API documentation: `docs/API.md`

## Getting Help

- 📚 Documentation: See `docs/` directory
- 🐛 Issues: GitHub Issues
- 💬 Discord: [Community Server](https://discord.gg/cryptoriskalert)
- 📧 Email: support@cryptoriskalert.io

## What's Next?

Check out:
- `docs/ARCHITECTURE.md` - System architecture details
- `docs/API.md` - Complete API reference
- `docs/DEPLOYMENT.md` - Production deployment guide
- `README.md` - Full project documentation

Happy monitoring! 🚀
