# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

API keys are required for production use:
```
Authorization: Bearer YOUR_API_KEY
```

## Rate Limits

| Tier | Requests/Day | Requests/Minute |
|------|--------------|-----------------|
| Free | 100 | 10 |
| Pro | 10,000 | 100 |
| Premium | 100,000 | 1,000 |
| Enterprise | Unlimited | Custom |

## Endpoints

### Health Check

#### GET /api/v1/health
Check API health status.

**Response:**
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

### Risk Assessment

#### GET /api/v1/risks/current
Get current risk assessments.

**Query Parameters:**
- `symbols` (array, optional): Filter by symbols
- `min_risk_level` (string, optional): Minimum risk level
- `network` (string, optional): Filter by network
- `limit` (integer, optional): Max results (default: 10, max: 100)

**Response:**
```json
[
  {
    "asset_symbol": "BTC",
    "overall_risk_score": 6.5,
    "risk_level": "high",
    "whale_risk_score": 7.2,
    "contract_risk_score": 0.0,
    "sentiment_risk_score": 5.8,
    "explanation": "Risk Level: HIGH (6.5/10)...",
    "recommendations": [
      "Monitor whale activity closely",
      "Consider reducing exposure"
    ],
    "timestamp": "2024-01-15T10:30:00Z",
    "confidence": 0.85
  }
]
```

#### GET /api/v1/risks/{symbol}
Get detailed risk assessment for specific asset.

**Path Parameters:**
- `symbol` (string, required): Asset symbol

**Query Parameters:**
- `network` (string, optional): Blockchain network
- `contract_address` (string, optional): Contract address

**Response:**
```json
{
  "asset_symbol": "ETH",
  "contract_address": "0x...",
  "network": "ethereum",
  "overall_risk_score": 4.2,
  "risk_level": "medium",
  "whale_risk_score": 3.5,
  "contract_risk_score": 5.0,
  "sentiment_risk_score": 4.0,
  "whale_transfers": [
    {
      "tx_hash": "0x...",
      "network": "ethereum",
      "from_address": "0x...",
      "to_address": "0x...",
      "amount": 1000.5,
      "token_symbol": "ETH",
      "usd_value": 2500000,
      "timestamp": "2024-01-15T10:00:00Z",
      "is_exchange": true,
      "exchange_name": "Binance"
    }
  ],
  "contract_analysis": {
    "contract_address": "0x...",
    "network": "ethereum",
    "risk_score": 5.0,
    "risk_level": "medium",
    "indicators": ["no_liquidity_lock"],
    "has_hidden_owner": false,
    "has_unlimited_mint": false,
    "liquidity_locked": false,
    "honeypot_risk": false,
    "owner_can_pause": true,
    "explanation": "Contract Risk Score: 5.0/10...",
    "analysis_timestamp": "2024-01-15T10:30:00Z"
  },
  "sentiment_data": [
    {
      "symbol": "ETH",
      "platform": "twitter",
      "sentiment_score": 0.3,
      "volume": 1500,
      "trending": true,
      "keywords": ["ethereum", "upgrade", "bullish"],
      "timestamp": "2024-01-15T10:30:00Z",
      "sample_texts": ["ETH looking strong!", "..."]
    }
  ],
  "explanation": "Risk Level: MEDIUM (4.2/10)...",
  "risk_factors": [
    "Liquidity is NOT locked - HIGH RUG PULL RISK",
    "Owner can pause trading"
  ],
  "recommendations": [
    "Verify liquidity lock before investing",
    "Monitor for owner actions"
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "confidence": 0.92
}
```

### Whale Transfers

#### GET /api/v1/whales/transfers
Get recent whale wallet transfers.

**Query Parameters:**
- `network` (string, required): Blockchain network (ethereum, bsc, polygon)
- `hours_back` (integer, optional): Hours to look back (default: 24, max: 168)
- `min_value_usd` (float, optional): Minimum USD value (default: 1000000)

**Response:**
```json
[
  {
    "tx_hash": "0xabc...",
    "network": "ethereum",
    "from_address": "0x123...",
    "to_address": "0x456...",
    "amount": 10000,
    "token_symbol": "ETH",
    "usd_value": 25000000,
    "timestamp": "2024-01-15T09:45:00Z",
    "is_exchange": true,
    "exchange_name": "Binance"
  }
]
```

### Contract Scanning

#### GET /api/v1/contracts/{address}/scan
Scan smart contract for security risks.

**Path Parameters:**
- `address` (string, required): Contract address

**Query Parameters:**
- `network` (string, required): Blockchain network

**Response:**
```json
{
  "contract_address": "0xabc...",
  "network": "ethereum",
  "risk_score": 7.5,
  "risk_level": "high",
  "indicators": [
    "no_liquidity_lock",
    "has_unlimited_mint",
    "owner_can_pause"
  ],
  "analysis_timestamp": "2024-01-15T10:30:00Z",
  "has_hidden_owner": false,
  "has_unlimited_mint": true,
  "liquidity_locked": false,
  "honeypot_risk": false,
  "owner_can_pause": true,
  "explanation": "Contract Risk Score: 7.5/10\n\n❌ Unlimited minting capability detected\n❌ Liquidity is NOT locked..."
}
```

### Sentiment Analysis

#### GET /api/v1/sentiment/{symbol}
Get sentiment analysis for crypto asset.

**Path Parameters:**
- `symbol` (string, required): Asset symbol

**Query Parameters:**
- `hours_back` (integer, optional): Hours to analyze (default: 24, max: 168)

**Response:**
```json
[
  {
    "symbol": "BTC",
    "platform": "twitter",
    "sentiment_score": 0.45,
    "volume": 2500,
    "trending": true,
    "keywords": ["bitcoin", "bullish", "moon", "buy"],
    "timestamp": "2024-01-15T10:30:00Z",
    "sample_texts": [
      "Bitcoin looking very bullish!",
      "BTC to the moon 🚀",
      "Just bought more BTC"
    ]
  },
  {
    "symbol": "BTC",
    "platform": "reddit",
    "sentiment_score": 0.35,
    "volume": 850,
    "trending": false,
    "keywords": ["bitcoin", "hodl", "analysis"],
    "timestamp": "2024-01-15T10:30:00Z",
    "sample_texts": [
      "BTC fundamentals still strong",
      "Long-term holder here, not selling"
    ]
  }
]
```

### Alert Subscription

#### POST /api/v1/alerts/subscribe
Subscribe to risk alerts.

**Request Body:**
```json
{
  "platform": "telegram",
  "chat_id": "123456789",
  "min_risk_level": "medium",
  "watched_assets": ["BTC", "ETH"],
  "networks": ["ethereum", "bsc"]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully subscribed to alerts",
  "subscription": {
    "user_id": "123456789",
    "platform": "telegram",
    "chat_id": "123456789",
    "min_risk_level": "medium",
    "watched_assets": ["BTC", "ETH"],
    "networks": ["ethereum", "bsc"],
    "active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "tier": "free"
  }
}
```

#### DELETE /api/v1/alerts/unsubscribe/{platform}/{user_id}
Unsubscribe from alerts.

**Path Parameters:**
- `platform` (string, required): Platform (telegram, discord, email)
- `user_id` (string, required): User ID

**Response:**
```json
{
  "status": "success",
  "message": "Successfully unsubscribed from alerts"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid parameters: symbol is required"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing API key"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Upgrade your plan for higher limits."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```

## Data Models

### RiskLevel Enum
- `critical`: 8.0+
- `high`: 6.0-7.9
- `medium`: 4.0-5.9
- `low`: 2.0-3.9
- `safe`: 0-1.9

### Network Enum
- `ethereum`
- `bsc`
- `polygon`
- `avalanche`
- `arbitrum`

## Code Examples

### Python
```python
import requests

API_URL = "http://localhost:8000/api/v1"
API_KEY = "your_api_key"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Get risk assessment
response = requests.get(
    f"{API_URL}/risks/BTC",
    headers=headers,
    params={"network": "ethereum"}
)

risk_data = response.json()
print(f"Risk Score: {risk_data['overall_risk_score']}")
```

### JavaScript
```javascript
const API_URL = "http://localhost:8000/api/v1";
const API_KEY = "your_api_key";

const headers = {
  "Authorization": `Bearer ${API_KEY}`
};

// Get whale transfers
fetch(`${API_URL}/whales/transfers?network=ethereum`, { headers })
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL
```bash
curl -X GET "http://localhost:8000/api/v1/risks/ETH" \
  -H "Authorization: Bearer your_api_key"
```

## Webhooks (Coming Soon)

Subscribe to webhook notifications for real-time alerts:

```json
{
  "webhook_url": "https://your-domain.com/webhook",
  "events": ["high_risk_alert", "whale_transfer", "contract_risk"],
  "secret": "your_webhook_secret"
}
```

## SDK Support (Coming Soon)

- Python SDK
- JavaScript/TypeScript SDK
- Go SDK
