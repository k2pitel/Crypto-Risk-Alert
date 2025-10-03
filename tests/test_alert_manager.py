"""Tests for Alert Manager."""

import pytest
from datetime import datetime
from src.core.alert_manager import AlertManager
from src.models.schemas import (
    RiskAssessment, RiskLevel, Network, 
    UserSubscription, WhaleTransfer
)


@pytest.fixture
def config():
    """Test configuration."""
    return {
        'alerts': {
            'telegram': {'enabled': True, 'bot_token': 'test_token'},
            'discord': {'enabled': True, 'bot_token': 'test_token'},
            'email': {'enabled': False}
        }
    }


@pytest.fixture
def alert_manager(config):
    """Create alert manager instance."""
    return AlertManager(config)


@pytest.fixture
def risk_assessment():
    """Sample risk assessment."""
    return RiskAssessment(
        asset_symbol="BTC",
        overall_risk_score=7.5,
        risk_level=RiskLevel.HIGH,
        whale_risk_score=8.0,
        contract_risk_score=0.0,
        sentiment_risk_score=6.5,
        explanation="High risk detected",
        risk_factors=["Large whale transfers", "Negative sentiment"],
        recommendations=["Consider reducing exposure"],
        timestamp=datetime.now(),
        confidence=0.85
    )


@pytest.mark.asyncio
async def test_create_alert(alert_manager, risk_assessment):
    """Test alert creation."""
    alert = await alert_manager.create_alert(
        alert_type='whale_transfer',
        risk_assessment=risk_assessment
    )
    
    assert alert.alert_type == 'whale_transfer'
    assert alert.risk_level == RiskLevel.HIGH
    assert alert.asset_symbol == "BTC"
    assert len(alert.title) > 0
    assert len(alert.message) > 0
    assert len(alert.channels) > 0


def test_add_remove_subscriber(alert_manager):
    """Test subscriber management."""
    subscription = UserSubscription(
        user_id="123",
        platform="telegram",
        chat_id="123",
        min_risk_level=RiskLevel.MEDIUM,
        active=True,
        created_at=datetime.now(),
        tier="free"
    )
    
    # Add subscriber
    alert_manager.add_subscriber(subscription)
    assert "telegram_123" in alert_manager.subscribers
    
    # Remove subscriber
    alert_manager.remove_subscriber("telegram", "123")
    assert "telegram_123" not in alert_manager.subscribers


@pytest.mark.asyncio
async def test_get_delivery_channels(alert_manager):
    """Test delivery channel selection based on risk level."""
    # Critical risk should use all channels
    channels_critical = alert_manager._get_delivery_channels(RiskLevel.CRITICAL)
    assert 'telegram' in channels_critical
    assert 'discord' in channels_critical
    
    # Low risk should use fewer channels
    channels_low = alert_manager._get_delivery_channels(RiskLevel.LOW)
    assert len(channels_low) <= len(channels_critical)


def test_get_subscribers_for_alert(alert_manager, risk_assessment):
    """Test subscriber filtering for alerts."""
    # Add subscribers with different preferences
    sub1 = UserSubscription(
        user_id="1",
        platform="telegram",
        chat_id="1",
        min_risk_level=RiskLevel.HIGH,
        watched_assets=["BTC"],
        active=True,
        created_at=datetime.now(),
        tier="free"
    )
    
    sub2 = UserSubscription(
        user_id="2",
        platform="telegram",
        chat_id="2",
        min_risk_level=RiskLevel.CRITICAL,  # Won't match HIGH risk
        watched_assets=["BTC"],
        active=True,
        created_at=datetime.now(),
        tier="free"
    )
    
    sub3 = UserSubscription(
        user_id="3",
        platform="telegram",
        chat_id="3",
        min_risk_level=RiskLevel.MEDIUM,
        watched_assets=["ETH"],  # Different asset
        active=True,
        created_at=datetime.now(),
        tier="free"
    )
    
    alert_manager.add_subscriber(sub1)
    alert_manager.add_subscriber(sub2)
    alert_manager.add_subscriber(sub3)
    
    alert = Alert(
        alert_id="test",
        alert_type="test",
        risk_level=RiskLevel.HIGH,
        title="Test",
        message="Test",
        asset_symbol="BTC",
        risk_assessment=risk_assessment,
        timestamp=datetime.now()
    )
    
    eligible = alert_manager.get_subscribers_for_alert(alert)
    
    # Only sub1 should match (right asset, right risk level)
    assert len(eligible) == 1
    assert eligible[0].user_id == "1"


def test_generate_alert_title(alert_manager, risk_assessment):
    """Test alert title generation."""
    title = alert_manager._generate_alert_title('whale_transfer', risk_assessment)
    assert 'BTC' in title
    assert len(title) > 0


def test_generate_alert_message(alert_manager, risk_assessment):
    """Test alert message generation."""
    # Add whale transfers to assessment
    risk_assessment.whale_transfers = [
        WhaleTransfer(
            tx_hash="0xabc",
            network=Network.ETHEREUM,
            from_address="0x123",
            to_address="0x456",
            amount=100,
            token_symbol="BTC",
            usd_value=5000000,
            timestamp=datetime.now(),
            is_exchange=True,
            exchange_name="Binance"
        )
    ]
    
    message = alert_manager._generate_alert_message('whale_transfer', risk_assessment)
    
    assert 'BTC' in message
    assert 'Risk Score' in message
    assert len(message) > 0


# Import Alert model
from src.models.schemas import Alert
