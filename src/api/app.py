"""FastAPI application for Crypto Risk Alert system."""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.models.schemas import (
    RiskAssessment, WhaleTransfer, ContractRisk, 
    SentimentData, Network, RiskLevel, UserSubscription
)
from src.core.risk_engine import RiskEngine
from src.services.blockchain_monitor import BlockchainMonitor
from src.services.contract_scanner import ContractScanner
from src.services.sentiment_analyzer import SentimentAnalyzer
from src.core.alert_manager import AlertManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto Risk Alert API",
    description="AI-powered cryptocurrency risk assessment and alerting system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services (in production, use dependency injection properly)
config = {}
risk_engine = None
blockchain_monitor = None
contract_scanner = None
sentiment_analyzer = None
alert_manager = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    import yaml
    
    global config, risk_engine, blockchain_monitor, contract_scanner, sentiment_analyzer, alert_manager
    
    try:
        with open('config/config.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        risk_engine = RiskEngine(config)
        blockchain_monitor = BlockchainMonitor(config)
        contract_scanner = ContractScanner(config)
        sentiment_analyzer = SentimentAnalyzer(config)
        alert_manager = AlertManager(config)
        
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")


# Request/Response models
class RiskAssessmentRequest(BaseModel):
    asset_symbol: str
    contract_address: Optional[str] = None
    network: Optional[Network] = None


class SubscriptionRequest(BaseModel):
    platform: str
    chat_id: str
    min_risk_level: RiskLevel = RiskLevel.MEDIUM
    watched_assets: List[str] = []
    networks: List[Network] = [Network.ETHEREUM]


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Crypto Risk Alert API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "risks": "/api/v1/risks/current",
            "whales": "/api/v1/whales/transfers",
            "contracts": "/api/v1/contracts/{address}/scan",
            "sentiment": "/api/v1/sentiment/{symbol}",
            "docs": "/docs"
        }
    }


@app.get("/api/v1/risks/current", response_model=List[RiskAssessment])
async def get_current_risks(
    symbols: Optional[List[str]] = Query(None),
    min_risk_level: Optional[RiskLevel] = None,
    network: Optional[Network] = None,
    limit: int = Query(10, le=100)
):
    """Get current risk assessments."""
    # In production, fetch from database/cache
    return []


@app.get("/api/v1/risks/{symbol}", response_model=RiskAssessment)
async def get_risk_assessment(
    symbol: str,
    network: Optional[Network] = None,
    contract_address: Optional[str] = None
):
    """Get detailed risk assessment for a specific asset."""
    
    try:
        # Fetch data from all sources
        whale_transfers = []
        if blockchain_monitor and network:
            whale_transfers = await blockchain_monitor.get_whale_transfers(
                network=network,
                hours_back=24
            )
        
        contract_analysis = None
        if contract_scanner and contract_address and network:
            contract_analysis = await contract_scanner.scan_contract(
                contract_address=contract_address,
                network=network
            )
        
        sentiment_data = []
        if sentiment_analyzer:
            sentiment_data = await sentiment_analyzer.analyze_sentiment(
                symbol=symbol,
                hours_back=24
            )
        
        # Calculate risk assessment
        assessment = risk_engine.assess_risk(
            asset_symbol=symbol,
            whale_transfers=whale_transfers,
            contract_analysis=contract_analysis,
            sentiment_data=sentiment_data,
            network=network,
            contract_address=contract_address
        )
        
        return assessment
        
    except Exception as e:
        logger.error(f"Error getting risk assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/whales/transfers", response_model=List[WhaleTransfer])
async def get_whale_transfers(
    network: Network = Network.ETHEREUM,
    hours_back: int = Query(24, le=168),
    min_value_usd: float = Query(1000000, ge=0)
):
    """Get recent whale wallet transfers."""
    
    try:
        if not blockchain_monitor:
            raise HTTPException(status_code=503, detail="Blockchain monitor not initialized")
        
        transfers = await blockchain_monitor.get_whale_transfers(
            network=network,
            min_value_usd=min_value_usd,
            hours_back=hours_back
        )
        
        return transfers
        
    except Exception as e:
        logger.error(f"Error fetching whale transfers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/contracts/{address}/scan", response_model=ContractRisk)
async def scan_contract(
    address: str,
    network: Network = Network.ETHEREUM
):
    """Scan a smart contract for security risks."""
    
    try:
        if not contract_scanner:
            raise HTTPException(status_code=503, detail="Contract scanner not initialized")
        
        result = await contract_scanner.scan_contract(
            contract_address=address,
            network=network
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error scanning contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sentiment/{symbol}", response_model=List[SentimentData])
async def get_sentiment(
    symbol: str,
    hours_back: int = Query(24, le=168)
):
    """Get sentiment analysis for a crypto asset."""
    
    try:
        if not sentiment_analyzer:
            raise HTTPException(status_code=503, detail="Sentiment analyzer not initialized")
        
        sentiment_data = await sentiment_analyzer.analyze_sentiment(
            symbol=symbol,
            hours_back=hours_back
        )
        
        return sentiment_data
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/alerts/subscribe")
async def subscribe_to_alerts(subscription: SubscriptionRequest):
    """Subscribe to risk alerts."""
    
    try:
        if not alert_manager:
            raise HTTPException(status_code=503, detail="Alert manager not initialized")
        
        user_subscription = UserSubscription(
            user_id=subscription.chat_id,  # In production, use proper user ID
            platform=subscription.platform,
            chat_id=subscription.chat_id,
            min_risk_level=subscription.min_risk_level,
            watched_assets=subscription.watched_assets,
            networks=subscription.networks,
            active=True,
            created_at=datetime.now(),
            tier='free'
        )
        
        alert_manager.add_subscriber(user_subscription)
        
        return {
            "status": "success",
            "message": "Successfully subscribed to alerts",
            "subscription": user_subscription.dict()
        }
        
    except Exception as e:
        logger.error(f"Error subscribing to alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/alerts/unsubscribe/{platform}/{user_id}")
async def unsubscribe_from_alerts(platform: str, user_id: str):
    """Unsubscribe from risk alerts."""
    
    try:
        if not alert_manager:
            raise HTTPException(status_code=503, detail="Alert manager not initialized")
        
        alert_manager.remove_subscriber(platform, user_id)
        
        return {
            "status": "success",
            "message": "Successfully unsubscribed from alerts"
        }
        
    except Exception as e:
        logger.error(f"Error unsubscribing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "risk_engine": risk_engine is not None,
            "blockchain_monitor": blockchain_monitor is not None,
            "contract_scanner": contract_scanner is not None,
            "sentiment_analyzer": sentiment_analyzer is not None,
            "alert_manager": alert_manager is not None
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
