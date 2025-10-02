# Crypto Risk Alert - Workflow Diagram

## System Workflow

### 1. Data Collection Flow

```
┌─────────────────────────────────────────────────────────┐
│                   EXTERNAL DATA SOURCES                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Blockchain  │  │    Social    │  │   Contract   │  │
│  │     APIs     │  │    Media     │  │  Explorers   │  │
│  │              │  │              │  │              │  │
│  │ • Etherscan  │  │  • Twitter   │  │ • Etherscan  │  │
│  │ • BSCScan    │  │  • Reddit    │  │ • Sourcify   │  │
│  │ • Web3       │  │  • Telegram  │  │ • BSCScan    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────┐
│              DATA COLLECTION SERVICES (Every 30s)        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         BlockchainMonitor                        │  │
│  │  • Fetch transactions                            │  │
│  │  • Filter whale transfers (> $1M USD)            │  │
│  │  • Identify exchange addresses                   │  │
│  │  • Calculate USD values                          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         SentimentAnalyzer (Every 5 min)          │  │
│  │  • Scrape social media posts                     │  │
│  │  • Perform NLP analysis                          │  │
│  │  • Calculate sentiment scores (-1 to 1)          │  │
│  │  • Extract trending keywords                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         ContractScanner (On-demand)              │  │
│  │  • Fetch contract source code                    │  │
│  │  • Analyze for rug-pull patterns                 │  │
│  │  • Check liquidity locks                         │  │
│  │  • Detect honeypot indicators                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
```

### 2. Risk Assessment Flow

```
┌─────────────────────────────────────────────────────────┐
│                    RISK ENGINE (Core AI)                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: Data Aggregation                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ Collect:                                        │    │
│  │  • Whale transfers (last 24h)                  │    │
│  │  • Contract analysis results                   │    │
│  │  • Sentiment data (last 6h)                    │    │
│  └────────────────────────────────────────────────┘    │
│                           │                              │
│                           ▼                              │
│  Step 2: Component Risk Calculation                      │
│  ┌────────────────────────────────────────────────┐    │
│  │ Whale Risk = f(volume, frequency, exchange)    │    │
│  │ Contract Risk = f(indicators, vulnerabilities) │    │
│  │ Sentiment Risk = f(score, volume, trending)    │    │
│  └────────────────────────────────────────────────┘    │
│                           │                              │
│                           ▼                              │
│  Step 3: Weighted Aggregation                            │
│  ┌────────────────────────────────────────────────┐    │
│  │ Overall Risk = 0.3 × Whale Risk +              │    │
│  │                0.4 × Contract Risk +           │    │
│  │                0.3 × Sentiment Risk            │    │
│  └────────────────────────────────────────────────┘    │
│                           │                              │
│                           ▼                              │
│  Step 4: Risk Level Classification                       │
│  ┌────────────────────────────────────────────────┐    │
│  │ CRITICAL: 8.0+ → Immediate action              │    │
│  │ HIGH:     6.0-7.9 → Significant risk           │    │
│  │ MEDIUM:   4.0-5.9 → Monitor closely            │    │
│  │ LOW:      2.0-3.9 → Low concern                │    │
│  │ SAFE:     0-1.9 → Minimal risk                 │    │
│  └────────────────────────────────────────────────┘    │
│                           │                              │
│                           ▼                              │
│  Step 5: Explainability Generation                       │
│  ┌────────────────────────────────────────────────┐    │
│  │ • Component breakdown                          │    │
│  │ • Key risk factors                             │    │
│  │ • Human-readable explanation                   │    │
│  │ • Actionable recommendations                   │    │
│  │ • Confidence score                             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
```

### 3. Alert Generation & Delivery Flow

```
┌─────────────────────────────────────────────────────────┐
│                   ALERT MANAGER                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: Alert Trigger Decision                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ IF risk_level >= MEDIUM:                       │    │
│  │   → Create Alert                               │    │
│  │ ELSE:                                          │    │
│  │   → Log only (dashboard)                       │    │
│  └────────────────────────────────────────────────┘    │
│                           │                              │
│                           ▼                              │
│  Step 2: Channel Selection                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ CRITICAL/HIGH → All channels                   │    │
│  │ MEDIUM → Telegram + Discord                    │    │
│  │ LOW → Telegram only                            │    │
│  └────────────────────────────────────────────────┘    │
│                           │                              │
│                           ▼                              │
│  Step 3: Subscriber Filtering                            │
│  ┌────────────────────────────────────────────────┐    │
│  │ Filter by:                                      │    │
│  │  • User's min risk level                       │    │
│  │  • Watched assets                              │    │
│  │  • Network preferences                         │    │
│  │  • Active subscription status                  │    │
│  └────────────────────────────────────────────────┘    │
│                           │                              │
│                           ▼                              │
│  Step 4: Message Formatting                              │
│  ┌────────────────────────────────────────────────┐    │
│  │ • Format for each platform                     │    │
│  │ • Add emojis and risk indicators               │    │
│  │ • Include risk breakdown                       │    │
│  │ • Provide recommendations                      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────┬───────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Telegram   │  │   Discord    │  │     Web      │
│     Bot      │  │     Bot      │  │  Dashboard   │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ • Direct msg │  │ • Channel    │  │ • Real-time  │
│ • Commands   │  │ • Rich embed │  │ • Historical │
│ • Interactive│  │ • Reactions  │  │ • Charts     │
└──────────────┘  └──────────────┘  └──────────────┘
      │                  │                  │
      ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────┐
│                      USERS                          │
│  Receive alerts → Review → Take Action              │
└─────────────────────────────────────────────────────┘
```

### 4. User Interaction Flow

```
┌─────────────────────────────────────────────────────────┐
│                  USER COMMANDS (Telegram/Discord)        │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┬──────────────┐
          ▼                ▼                ▼              ▼
    /subscribe         /watch BTC        /risk ETH     /status
          │                │                │              │
          ▼                ▼                ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Create     │  │   Add to     │  │   Fetch      │  │   Show       │
│ Subscription │  │  Watchlist   │  │   Risk       │  │Subscription  │
│              │  │              │  │  Assessment  │  │   Status     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│              ALERT MANAGER / API LAYER                      │
│  • Store preferences                                        │
│  • Validate input                                           │
│  • Execute request                                          │
│  • Return formatted response                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Response   │
                    │   to User    │
                    └──────────────┘
```

### 5. Continuous Monitoring Loop

```
                    START SYSTEM
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  Initialize All Services        │
        │  • Risk Engine                  │
        │  • Blockchain Monitor           │
        │  • Sentiment Analyzer           │
        │  • Contract Scanner             │
        │  • Alert Manager                │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   Start Monitoring Loops       │
        └────────────┬───────────────────┘
                     │
        ┌────────────┴───────────────┐
        │                            │
        ▼                            ▼
┌──────────────────┐        ┌──────────────────┐
│ Blockchain Loop  │        │ Sentiment Loop   │
│ (Every 30 sec)   │        │ (Every 5 min)    │
└────────┬─────────┘        └────────┬─────────┘
         │                           │
         ▼                           ▼
    Whale Transfer               Sentiment
    Detected?                    Changed?
         │                           │
         └──────┬────────────────────┘
                │
          Yes   ▼   No
        ┌──────────────┐
        │ Risk Engine  │
        │  Calculate   │
        └──────┬───────┘
               │
         High Risk?
               │
          Yes  ▼  No
        ┌──────────────┐
        │Create & Send │
        │    Alert     │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │  Continue    │
        │  Monitoring  │
        └──────┬───────┘
               │
               └──────→ (Loop back to monitoring)
```

## Key Timing Parameters

| Service | Interval | Purpose |
|---------|----------|---------|
| Blockchain Monitor | 30 seconds | Real-time whale detection |
| Sentiment Analyzer | 5 minutes | Social media trends |
| Contract Scanner | On-demand | Per request/scheduled |
| Alert Delivery | Immediate | Critical alerts |
| API Rate Limits | Tier-based | Prevent abuse |
| Cache TTL | 5 minutes | Reduce API calls |

## Data Persistence

```
┌──────────────────────────────────────────┐
│         PostgreSQL Database              │
├──────────────────────────────────────────┤
│ • User subscriptions                     │
│ • Alert history                          │
│ • Risk assessments (archive)             │
│ • API usage logs                         │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│            Redis Cache                   │
├──────────────────────────────────────────┤
│ • Recent risk scores (5 min TTL)         │
│ • API rate limits                        │
│ • Active sessions                        │
│ • Temporary data                         │
└──────────────────────────────────────────┘
```

## Error Handling Flow

```
Error Occurs
    │
    ▼
┌──────────────┐
│  Log Error   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Error Type?          │
└──────┬───────────────┘
       │
   ┌───┴────┬────────┬────────┐
   ▼        ▼        ▼        ▼
API     Network   Config   Internal
Error   Error     Error    Error
   │        │        │        │
   ▼        ▼        ▼        ▼
Retry   Wait &    Notify   Fallback
(3x)    Retry     Admin    Mode
   │        │        │        │
   └────────┴────────┴────────┘
            │
            ▼
     Continue/Alert
```

This workflow ensures:
- ✅ Real-time risk detection
- ✅ Accurate alert delivery
- ✅ User preference handling
- ✅ System reliability
- ✅ Error resilience
