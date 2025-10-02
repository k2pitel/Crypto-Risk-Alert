"""Core data models for the Crypto Risk Alert system."""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"


class Network(str, Enum):
    """Blockchain network enumeration."""
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    ARBITRUM = "arbitrum"


class WhaleTransfer(BaseModel):
    """Model for whale wallet transfer data."""
    tx_hash: str
    network: Network
    from_address: str
    to_address: str
    amount: float
    token_symbol: str
    usd_value: float
    timestamp: datetime
    is_exchange: bool = False
    exchange_name: Optional[str] = None


class ContractRisk(BaseModel):
    """Model for smart contract risk assessment."""
    contract_address: str
    network: Network
    risk_score: float = Field(ge=0, le=10)
    risk_level: RiskLevel
    indicators: List[str] = []
    analysis_timestamp: datetime
    
    # Detailed analysis
    has_hidden_owner: bool = False
    has_unlimited_mint: bool = False
    liquidity_locked: bool = True
    honeypot_risk: bool = False
    owner_can_pause: bool = False
    
    explanation: str = ""


class SentimentData(BaseModel):
    """Model for sentiment analysis data."""
    symbol: str
    platform: str  # twitter, reddit, telegram
    sentiment_score: float = Field(ge=-1, le=1)
    volume: int  # number of mentions
    trending: bool = False
    keywords: List[str] = []
    timestamp: datetime
    sample_texts: List[str] = []


class RiskAssessment(BaseModel):
    """Comprehensive risk assessment model."""
    asset_symbol: str
    contract_address: Optional[str] = None
    network: Optional[Network] = None
    
    overall_risk_score: float = Field(ge=0, le=10)
    risk_level: RiskLevel
    
    # Component scores
    whale_risk_score: float = 0.0
    contract_risk_score: float = 0.0
    sentiment_risk_score: float = 0.0
    
    # Contributing factors
    whale_transfers: List[WhaleTransfer] = []
    contract_analysis: Optional[ContractRisk] = None
    sentiment_data: List[SentimentData] = []
    
    # Explainability
    explanation: str
    risk_factors: List[str] = []
    recommendations: List[str] = []
    
    timestamp: datetime
    confidence: float = Field(ge=0, le=1)


class Alert(BaseModel):
    """Alert model for notifications."""
    alert_id: str
    alert_type: str  # whale_transfer, contract_risk, sentiment_shift
    risk_level: RiskLevel
    
    title: str
    message: str
    
    asset_symbol: str
    contract_address: Optional[str] = None
    network: Optional[Network] = None
    
    risk_assessment: RiskAssessment
    
    channels: List[str] = ["telegram", "discord"]  # delivery channels
    delivered: bool = False
    timestamp: datetime


class UserSubscription(BaseModel):
    """User subscription model."""
    user_id: str
    platform: str  # telegram, discord, email
    chat_id: str
    
    # Preferences
    min_risk_level: RiskLevel = RiskLevel.MEDIUM
    watched_assets: List[str] = []
    watched_contracts: List[str] = []
    networks: List[Network] = [Network.ETHEREUM]
    
    active: bool = True
    created_at: datetime
    tier: str = "free"  # free, pro, premium


class APIUsage(BaseModel):
    """API usage tracking."""
    api_key: str
    user_id: str
    endpoint: str
    timestamp: datetime
    tier: str
    rate_limit_remaining: int
