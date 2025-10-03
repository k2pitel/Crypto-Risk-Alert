# Crypto Risk Alert System - Architecture Documentation

## System Overview

The Crypto Risk Alert System is an AI-powered platform designed to detect and alert users about cryptocurrency risks in real-time. The system monitors blockchain activity, analyzes smart contracts, tracks social sentiment, and delivers actionable alerts through multiple channels.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
├─────────────────────────────────────────────────────────────────┤
│  Blockchain APIs    │  Social Media    │  Contract Explorers    │
│  (Etherscan, etc)   │  (Twitter, Reddit)│  (Sourcify, etc)      │
└──────────┬─────────────────┬─────────────────┬──────────────────┘
           │                 │                 │
           ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA COLLECTION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  BlockchainMonitor  │  SentimentAnalyzer │  ContractScanner    │
│  - Whale tracking   │  - NLP analysis     │  - Code analysis    │
│  - Tx monitoring    │  - Keyword extract  │  - Rug-pull detect  │
└──────────┬─────────────────┬─────────────────┬──────────────────┘
           │                 │                 │
           └────────────────┬┴─────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RISK ENGINE (Core AI)                       │
├─────────────────────────────────────────────────────────────────┤
│  • Aggregates data from all sources                             │
│  • Calculates weighted risk scores                              │
│  • Provides explainable AI insights                             │
│  • Generates recommendations                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ALERT MANAGER                              │
├─────────────────────────────────────────────────────────────────┤
│  • Manages alert priorities                                      │
│  • Handles user subscriptions                                    │
│  • Routes alerts to appropriate channels                         │
└──────────┬─────────────────┬─────────────────┬──────────────────┘
           │                 │                 │
           ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DELIVERY CHANNELS                           │
├─────────────────────────────────────────────────────────────────┤
│   Telegram Bot      │   Discord Bot    │   Web Dashboard        │
│   - Real-time alerts│   - Embeds       │   - Historical data    │
│   - Commands        │   - Commands     │   - Visualizations     │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Collection Layer

#### Blockchain Monitor (`src/services/blockchain_monitor.py`)
- **Purpose**: Track whale wallet transfers and on-chain activity
- **Data Sources**: Etherscan, BSCScan, Polygonscan APIs
- **Key Features**:
  - Multi-chain support (Ethereum, BSC, Polygon)
  - Configurable whale thresholds
  - Exchange address detection
  - Real-time monitoring (30-second intervals)

#### Sentiment Analyzer (`src/services/sentiment_analyzer.py`)
- **Purpose**: Analyze social media sentiment
- **Data Sources**: Twitter API, Reddit API, Telegram channels
- **Key Features**:
  - Multi-platform sentiment tracking
  - Keyword extraction
  - Trending detection
  - NLP-based scoring

#### Contract Scanner (`src/services/contract_scanner.py`)
- **Purpose**: Detect smart contract vulnerabilities
- **Data Sources**: Contract source code from explorers
- **Key Features**:
  - Rug-pull pattern detection
  - Honeypot identification
  - Liquidity lock verification
  - Owner privilege analysis

### 2. Risk Engine

#### Core Risk Engine (`src/core/risk_engine.py`)
- **Purpose**: Calculate comprehensive risk scores with explainability
- **Algorithm**:
  ```python
  overall_risk = (
      whale_risk * 0.3 +
      contract_risk * 0.4 +
      sentiment_risk * 0.3
  )
  ```
- **Risk Levels**:
  - CRITICAL: 8.0+ (immediate action required)
  - HIGH: 6.0-7.9 (significant risk)
  - MEDIUM: 4.0-5.9 (monitor closely)
  - LOW: 2.0-3.9 (low concern)
  - SAFE: 0-1.9 (minimal risk)

- **Explainability Features**:
  - Detailed risk factor breakdown
  - Human-readable explanations
  - Actionable recommendations
  - Confidence scores

### 3. Alert Management

#### Alert Manager (`src/core/alert_manager.py`)
- **Purpose**: Manage alert lifecycle and delivery
- **Features**:
  - Multi-channel delivery
  - Priority-based routing
  - User subscription management
  - Alert deduplication

### 4. Delivery Channels

#### Telegram Bot (`src/bots/telegram_bot.py`)
- Commands: /start, /subscribe, /watch, /risk, /status
- Real-time push notifications
- Interactive commands

#### Discord Bot (`src/bots/discord_bot.py`)
- Commands: !start, !subscribe, !watch, !risk, !status
- Rich embeds with color coding
- Server integration

#### Web Dashboard (Future)
- Historical risk data
- Interactive charts
- Portfolio tracking

### 5. API Layer

#### REST API (`src/api/app.py`)
- **Framework**: FastAPI
- **Endpoints**:
  - `GET /api/v1/risks/current` - Current risk assessments
  - `GET /api/v1/risks/{symbol}` - Detailed risk for asset
  - `GET /api/v1/whales/transfers` - Recent whale activity
  - `GET /api/v1/contracts/{address}/scan` - Contract scan
  - `GET /api/v1/sentiment/{symbol}` - Sentiment data
  - `POST /api/v1/alerts/subscribe` - Subscribe to alerts

## Data Flow

### 1. Data Collection Flow
```
Blockchain → API Call → Parse Response → Normalize Data → Store/Cache
Social Media → Scrape/API → NLP Analysis → Sentiment Score → Store/Cache
Contracts → Fetch Source → Analyze Code → Risk Indicators → Store/Cache
```

### 2. Risk Assessment Flow
```
Trigger Event → Fetch Related Data → Calculate Component Risks →
Apply Weights → Generate Explanation → Determine Alert Priority →
Create Alert → Route to Channels → Deliver to Users
```

### 3. Alert Delivery Flow
```
Alert Created → Check User Subscriptions → Filter by Preferences →
Format for Channel → Send via Bot/API → Track Delivery Status
```

## Technology Stack

### Backend
- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **Async**: asyncio, aiohttp
- **Data Models**: Pydantic

### Blockchain Integration
- **Web3**: web3.py
- **APIs**: Etherscan, BSCScan, Polygonscan

### AI/ML
- **NLP**: transformers, NLTK
- **ML**: scikit-learn, numpy, pandas
- **Deep Learning**: PyTorch

### Data Storage
- **Database**: PostgreSQL
- **Cache**: Redis
- **Message Queue**: Celery

### Bots & Notifications
- **Telegram**: python-telegram-bot
- **Discord**: discord.py
- **Email**: SMTP

### Deployment
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions

## Scalability Considerations

### Horizontal Scaling
- Stateless API services
- Message queue for async processing
- Load balancing for API endpoints

### Data Management
- Redis caching for frequently accessed data
- PostgreSQL for persistent storage
- Time-series DB for historical metrics

### Performance Optimization
- API rate limiting
- Response caching
- Batch processing for alerts
- WebSocket for real-time updates

## Security

### API Security
- API key authentication
- Rate limiting per tier
- HTTPS/TLS encryption
- Input validation

### Data Security
- Encrypted storage for sensitive data
- No storage of private keys
- Secure API key management
- Regular security audits

### Bot Security
- Webhook verification (Telegram)
- Token validation (Discord)
- Command rate limiting
- User authorization

## Monitoring & Logging

### Application Monitoring
- Health check endpoints
- Error tracking
- Performance metrics
- User analytics

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation
- Alert on critical errors

## Deployment Architecture

### Development
```
Local Machine → Python venv → Config files → Local services
```

### Staging
```
Docker Compose → Multi-container setup → Test APIs → Staging DB
```

### Production
```
Kubernetes Cluster → Auto-scaling → Load Balancer → Production DB
                   → Monitoring → Alerts → Backups
```

## Future Enhancements

### Phase 2: Advanced Analytics
- Machine learning models for risk prediction
- Historical pattern analysis
- Cross-chain correlation analysis
- Advanced NLP with transformers

### Phase 3: Portfolio Management
- Portfolio tracking integration
- Personal risk dashboards
- Automated rebalancing suggestions
- DeFi protocol monitoring

### Phase 4: Enterprise Features
- White-label solutions
- Custom integrations
- SLA guarantees
- On-premise deployment
