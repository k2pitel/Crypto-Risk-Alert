"""Tests for Risk Engine."""

import pytest
from datetime import datetime, timedelta
from src.core.risk_engine import RiskEngine
from src.models.schemas import (
    WhaleTransfer, ContractRisk, SentimentData, 
    Network, RiskLevel
)


@pytest.fixture
def config():
    """Test configuration."""
    return {
        'risk_scoring': {
            'weights': {
                'whale_transfer': 0.3,
                'contract_analysis': 0.4,
                'sentiment': 0.3
            },
            'thresholds': {
                'critical': 8.0,
                'high': 6.0,
                'medium': 4.0,
                'low': 2.0
            }
        }
    }


@pytest.fixture
def risk_engine(config):
    """Create risk engine instance."""
    return RiskEngine(config)


def test_calculate_whale_risk_no_transfers(risk_engine):
    """Test whale risk calculation with no transfers."""
    score, explanations = risk_engine.calculate_whale_risk([])
    assert score == 0.0
    assert len(explanations) == 0


def test_calculate_whale_risk_high_value(risk_engine):
    """Test whale risk with high value transfers."""
    transfers = [
        WhaleTransfer(
            tx_hash="0xabc",
            network=Network.ETHEREUM,
            from_address="0x123",
            to_address="0x456",
            amount=1000,
            token_symbol="ETH",
            usd_value=10_000_000,
            timestamp=datetime.now(),
            is_exchange=True,
            exchange_name="Binance"
        )
    ]
    
    score, explanations = risk_engine.calculate_whale_risk(transfers)
    assert score > 0
    assert any('transfer volume' in exp.lower() for exp in explanations)


def test_calculate_contract_risk_safe(risk_engine):
    """Test contract risk for safe contract."""
    contract = ContractRisk(
        contract_address="0xabc",
        network=Network.ETHEREUM,
        risk_score=1.0,
        risk_level=RiskLevel.LOW,
        indicators=[],
        analysis_timestamp=datetime.now(),
        has_hidden_owner=False,
        has_unlimited_mint=False,
        liquidity_locked=True,
        honeypot_risk=False,
        owner_can_pause=False,
        explanation="Safe contract"
    )
    
    score, explanations = risk_engine.calculate_contract_risk(contract)
    assert score == 1.0
    assert len(explanations) == 0


def test_calculate_contract_risk_dangerous(risk_engine):
    """Test contract risk for dangerous contract."""
    contract = ContractRisk(
        contract_address="0xabc",
        network=Network.ETHEREUM,
        risk_score=9.0,
        risk_level=RiskLevel.CRITICAL,
        indicators=['no_liquidity_lock', 'has_unlimited_mint'],
        analysis_timestamp=datetime.now(),
        has_hidden_owner=False,
        has_unlimited_mint=True,
        liquidity_locked=False,
        honeypot_risk=False,
        owner_can_pause=True,
        explanation="Dangerous contract"
    )
    
    score, explanations = risk_engine.calculate_contract_risk(contract)
    assert score == 9.0
    assert len(explanations) > 0
    assert any('liquidity' in exp.lower() for exp in explanations)


def test_calculate_sentiment_risk_positive(risk_engine):
    """Test sentiment risk with positive sentiment."""
    sentiment_data = [
        SentimentData(
            symbol="BTC",
            platform="twitter",
            sentiment_score=0.8,
            volume=1000,
            trending=True,
            keywords=["bullish", "moon"],
            timestamp=datetime.now(),
            sample_texts=["BTC to the moon!"]
        )
    ]
    
    score, explanations = risk_engine.calculate_sentiment_risk(sentiment_data)
    assert score < 5.0  # Positive sentiment = low risk


def test_calculate_sentiment_risk_negative(risk_engine):
    """Test sentiment risk with negative sentiment."""
    sentiment_data = [
        SentimentData(
            symbol="BTC",
            platform="twitter",
            sentiment_score=-0.8,
            volume=2000,
            trending=True,
            keywords=["crash", "dump", "scam"],
            timestamp=datetime.now(),
            sample_texts=["BTC is crashing!"]
        )
    ]
    
    score, explanations = risk_engine.calculate_sentiment_risk(sentiment_data)
    assert score > 5.0  # Negative sentiment = high risk
    assert len(explanations) > 0


def test_assess_risk_comprehensive(risk_engine):
    """Test comprehensive risk assessment."""
    whale_transfers = [
        WhaleTransfer(
            tx_hash="0xabc",
            network=Network.ETHEREUM,
            from_address="0x123",
            to_address="0x456",
            amount=1000,
            token_symbol="ETH",
            usd_value=5_000_000,
            timestamp=datetime.now(),
            is_exchange=True,
            exchange_name="Binance"
        )
    ]
    
    contract_analysis = ContractRisk(
        contract_address="0xabc",
        network=Network.ETHEREUM,
        risk_score=6.0,
        risk_level=RiskLevel.HIGH,
        indicators=['no_liquidity_lock'],
        analysis_timestamp=datetime.now(),
        has_hidden_owner=False,
        has_unlimited_mint=False,
        liquidity_locked=False,
        honeypot_risk=False,
        owner_can_pause=False,
        explanation="Medium risk"
    )
    
    sentiment_data = [
        SentimentData(
            symbol="ETH",
            platform="twitter",
            sentiment_score=-0.5,
            volume=1500,
            trending=True,
            keywords=["dump", "sell"],
            timestamp=datetime.now(),
            sample_texts=["Selling my ETH"]
        )
    ]
    
    assessment = risk_engine.assess_risk(
        asset_symbol="ETH",
        whale_transfers=whale_transfers,
        contract_analysis=contract_analysis,
        sentiment_data=sentiment_data,
        network=Network.ETHEREUM,
        contract_address="0xabc"
    )
    
    assert assessment.asset_symbol == "ETH"
    assert assessment.overall_risk_score > 0
    assert assessment.risk_level in RiskLevel
    assert len(assessment.explanation) > 0
    assert len(assessment.recommendations) > 0
    assert 0 <= assessment.confidence <= 1


def test_risk_level_mapping(risk_engine):
    """Test risk level determination."""
    assert risk_engine._get_risk_level(9.0) == RiskLevel.CRITICAL
    assert risk_engine._get_risk_level(7.0) == RiskLevel.HIGH
    assert risk_engine._get_risk_level(5.0) == RiskLevel.MEDIUM
    assert risk_engine._get_risk_level(3.0) == RiskLevel.LOW
    assert risk_engine._get_risk_level(1.0) == RiskLevel.SAFE


def test_confidence_calculation(risk_engine):
    """Test confidence score calculation."""
    # All data available
    confidence = risk_engine._calculate_confidence(
        whale_transfers=[WhaleTransfer(
            tx_hash="0x", network=Network.ETHEREUM,
            from_address="0x", to_address="0x",
            amount=1, token_symbol="ETH", usd_value=1,
            timestamp=datetime.now()
        )],
        contract_analysis=ContractRisk(
            contract_address="0x", network=Network.ETHEREUM,
            risk_score=1, risk_level=RiskLevel.LOW,
            analysis_timestamp=datetime.now()
        ),
        sentiment_data=[SentimentData(
            symbol="ETH", platform="twitter",
            sentiment_score=0, volume=1,
            timestamp=datetime.now()
        )]
    )
    assert confidence > 0.5
    
    # No data
    confidence_empty = risk_engine._calculate_confidence([], None, [])
    assert confidence_empty == 0.0
