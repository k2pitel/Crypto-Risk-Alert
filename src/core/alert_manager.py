"""Alert management system for delivering risk alerts."""

import logging
from datetime import datetime
from typing import List, Dict
import asyncio
from src.models.schemas import Alert, RiskAssessment, RiskLevel, UserSubscription

logger = logging.getLogger(__name__)


class AlertManager:
    """Manage and deliver risk alerts across multiple channels."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.alert_config = config.get('alerts', {})
        self.subscribers = {}  # In production, use database
        self.alert_queue = asyncio.Queue()
    
    async def create_alert(
        self,
        alert_type: str,
        risk_assessment: RiskAssessment,
        title: str = None,
        message: str = None
    ) -> Alert:
        """Create a new alert from risk assessment."""
        
        # Generate alert ID
        alert_id = f"{alert_type}_{risk_assessment.asset_symbol}_{int(datetime.now().timestamp())}"
        
        # Generate title and message if not provided
        if not title:
            title = self._generate_alert_title(alert_type, risk_assessment)
        
        if not message:
            message = self._generate_alert_message(alert_type, risk_assessment)
        
        # Determine delivery channels based on risk level
        channels = self._get_delivery_channels(risk_assessment.risk_level)
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            risk_level=risk_assessment.risk_level,
            title=title,
            message=message,
            asset_symbol=risk_assessment.asset_symbol,
            contract_address=risk_assessment.contract_address,
            network=risk_assessment.network,
            risk_assessment=risk_assessment,
            channels=channels,
            delivered=False,
            timestamp=datetime.now()
        )
        
        return alert
    
    async def send_alert(self, alert: Alert):
        """Send alert through configured channels."""
        
        logger.info(f"Sending {alert.risk_level.value} alert for {alert.asset_symbol}")
        
        delivery_results = {}
        
        for channel in alert.channels:
            try:
                if channel == 'telegram' and self.alert_config.get('telegram', {}).get('enabled'):
                    result = await self._send_telegram_alert(alert)
                    delivery_results['telegram'] = result
                
                elif channel == 'discord' and self.alert_config.get('discord', {}).get('enabled'):
                    result = await self._send_discord_alert(alert)
                    delivery_results['discord'] = result
                
                elif channel == 'email' and self.alert_config.get('email', {}).get('enabled'):
                    result = await self._send_email_alert(alert)
                    delivery_results['email'] = result
                
            except Exception as e:
                logger.error(f"Error sending alert via {channel}: {e}")
                delivery_results[channel] = False
        
        alert.delivered = any(delivery_results.values())
        
        return delivery_results
    
    async def _send_telegram_alert(self, alert: Alert) -> bool:
        """Send alert via Telegram."""
        # This would be implemented by the Telegram bot
        # For now, just log
        logger.info(f"[TELEGRAM] {alert.title}: {alert.message[:100]}...")
        return True
    
    async def _send_discord_alert(self, alert: Alert) -> bool:
        """Send alert via Discord."""
        # This would be implemented by the Discord bot
        logger.info(f"[DISCORD] {alert.title}: {alert.message[:100]}...")
        return True
    
    async def _send_email_alert(self, alert: Alert) -> bool:
        """Send alert via Email."""
        # Implement email sending using SMTP
        logger.info(f"[EMAIL] {alert.title}: {alert.message[:100]}...")
        return True
    
    def _generate_alert_title(
        self, 
        alert_type: str, 
        risk_assessment: RiskAssessment
    ) -> str:
        """Generate alert title."""
        
        emoji_map = {
            RiskLevel.CRITICAL: "🚨",
            RiskLevel.HIGH: "⚠️",
            RiskLevel.MEDIUM: "⚡",
            RiskLevel.LOW: "ℹ️",
            RiskLevel.SAFE: "✅"
        }
        
        emoji = emoji_map.get(risk_assessment.risk_level, "📢")
        
        if alert_type == 'whale_transfer':
            return f"{emoji} Whale Alert: {risk_assessment.asset_symbol}"
        elif alert_type == 'contract_risk':
            return f"{emoji} Contract Risk: {risk_assessment.asset_symbol}"
        elif alert_type == 'sentiment_shift':
            return f"{emoji} Sentiment Alert: {risk_assessment.asset_symbol}"
        elif alert_type == 'risk_assessment':
            return f"{emoji} Risk Alert: {risk_assessment.asset_symbol}"
        else:
            return f"{emoji} Alert: {risk_assessment.asset_symbol}"
    
    def _generate_alert_message(
        self, 
        alert_type: str, 
        risk_assessment: RiskAssessment
    ) -> str:
        """Generate detailed alert message."""
        
        message = f"**{risk_assessment.asset_symbol}** - {risk_assessment.risk_level.value.upper()} Risk\n\n"
        
        # Add risk score
        message += f"🎯 Risk Score: {risk_assessment.overall_risk_score}/10\n\n"
        
        # Add main explanation
        message += f"**Analysis:**\n{risk_assessment.explanation}\n\n"
        
        # Add specific alert type information
        if alert_type == 'whale_transfer' and risk_assessment.whale_transfers:
            transfers = risk_assessment.whale_transfers[:3]
            message += "**Recent Whale Transfers:**\n"
            for transfer in transfers:
                message += f"• ${transfer.usd_value:,.0f} to {'Exchange' if transfer.is_exchange else 'Wallet'}\n"
            message += "\n"
        
        if alert_type == 'contract_risk' and risk_assessment.contract_analysis:
            message += "**Contract Issues:**\n"
            for indicator in risk_assessment.contract_analysis.indicators[:5]:
                message += f"• {indicator.replace('_', ' ').title()}\n"
            message += "\n"
        
        if alert_type == 'sentiment_shift' and risk_assessment.sentiment_data:
            avg_sentiment = sum(s.sentiment_score for s in risk_assessment.sentiment_data) / len(risk_assessment.sentiment_data)
            message += f"**Sentiment Score:** {avg_sentiment:.2f}\n"
            message += f"**Discussion Volume:** {sum(s.volume for s in risk_assessment.sentiment_data)} mentions\n\n"
        
        # Add recommendations
        if risk_assessment.recommendations:
            message += "**Recommendations:**\n"
            for rec in risk_assessment.recommendations[:3]:
                message += f"• {rec}\n"
        
        return message
    
    def _get_delivery_channels(self, risk_level: RiskLevel) -> List[str]:
        """Determine which channels to use based on risk level."""
        
        channels = []
        
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            # Critical/High risk: all channels
            if self.alert_config.get('telegram', {}).get('enabled'):
                channels.append('telegram')
            if self.alert_config.get('discord', {}).get('enabled'):
                channels.append('discord')
            if self.alert_config.get('email', {}).get('enabled'):
                channels.append('email')
        
        elif risk_level == RiskLevel.MEDIUM:
            # Medium risk: Telegram and Discord
            if self.alert_config.get('telegram', {}).get('enabled'):
                channels.append('telegram')
            if self.alert_config.get('discord', {}).get('enabled'):
                channels.append('discord')
        
        else:
            # Low risk: Dashboard only (Telegram for info)
            if self.alert_config.get('telegram', {}).get('enabled'):
                channels.append('telegram')
        
        return channels if channels else ['telegram']  # Default to telegram
    
    def add_subscriber(self, subscription: UserSubscription):
        """Add a new subscriber."""
        key = f"{subscription.platform}_{subscription.user_id}"
        self.subscribers[key] = subscription
        logger.info(f"Added subscriber: {key}")
    
    def remove_subscriber(self, platform: str, user_id: str):
        """Remove a subscriber."""
        key = f"{platform}_{user_id}"
        if key in self.subscribers:
            del self.subscribers[key]
            logger.info(f"Removed subscriber: {key}")
    
    def get_subscribers_for_alert(self, alert: Alert) -> List[UserSubscription]:
        """Get subscribers who should receive this alert."""
        
        eligible_subscribers = []
        
        for sub in self.subscribers.values():
            # Check if subscriber is active
            if not sub.active:
                continue
            
            # Check risk level threshold
            risk_levels_order = [
                RiskLevel.SAFE,
                RiskLevel.LOW,
                RiskLevel.MEDIUM,
                RiskLevel.HIGH,
                RiskLevel.CRITICAL
            ]
            
            min_index = risk_levels_order.index(sub.min_risk_level)
            alert_index = risk_levels_order.index(alert.risk_level)
            
            if alert_index < min_index:
                continue
            
            # Check if watching this asset
            if sub.watched_assets and alert.asset_symbol not in sub.watched_assets:
                continue
            
            # Check if watching this contract
            if sub.watched_contracts and alert.contract_address:
                if alert.contract_address not in sub.watched_contracts:
                    continue
            
            # Check network
            if alert.network and sub.networks:
                if alert.network not in sub.networks:
                    continue
            
            eligible_subscribers.append(sub)
        
        return eligible_subscribers
