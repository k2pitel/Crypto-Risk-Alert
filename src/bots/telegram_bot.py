"""Telegram bot for delivering crypto risk alerts."""

import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes,
    MessageHandler,
    filters
)
from src.models.schemas import UserSubscription, RiskLevel, Network, Alert
from src.core.alert_manager import AlertManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for crypto risk alerts."""
    
    def __init__(self, config: dict, alert_manager: AlertManager):
        self.config = config
        self.alert_manager = alert_manager
        self.bot_token = config.get('alerts', {}).get('telegram', {}).get('bot_token')
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        
        welcome_message = """
🚀 **Welcome to Crypto Risk Alert Bot!**

I help you monitor cryptocurrency risks including:
• 🐋 Whale wallet transfers
• 🔒 Smart contract vulnerabilities
• 📊 Social sentiment analysis

**Commands:**
/start - Show this message
/subscribe - Subscribe to alerts
/unsubscribe - Unsubscribe from alerts
/status - Check your subscription status
/watch <symbol> - Watch a specific crypto (e.g., /watch BTC)
/unwatch <symbol> - Stop watching a crypto
/risk <symbol> - Get current risk assessment
/settings - Configure alert preferences
/help - Show help message

Get started by subscribing: /subscribe
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command."""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        
        # Create subscription
        subscription = UserSubscription(
            user_id=user_id,
            platform='telegram',
            chat_id=chat_id,
            min_risk_level=RiskLevel.MEDIUM,
            watched_assets=[],
            networks=[Network.ETHEREUM],
            active=True,
            created_at=datetime.now(),
            tier='free'
        )
        
        self.alert_manager.add_subscriber(subscription)
        
        message = """
✅ **Successfully subscribed to Crypto Risk Alerts!**

You will receive alerts for:
• Risk Level: MEDIUM and above
• Networks: Ethereum
• All assets (use /watch to focus on specific assets)

Configure your preferences: /settings
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command."""
        user_id = str(update.effective_user.id)
        
        self.alert_manager.remove_subscriber('telegram', user_id)
        
        await update.message.reply_text(
            "❌ You have been unsubscribed from alerts.\n\n"
            "Subscribe again anytime with /subscribe"
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user_id = str(update.effective_user.id)
        
        key = f"telegram_{user_id}"
        subscription = self.alert_manager.subscribers.get(key)
        
        if not subscription:
            await update.message.reply_text(
                "You are not subscribed. Use /subscribe to get started."
            )
            return
        
        watched = ', '.join(subscription.watched_assets) if subscription.watched_assets else 'All'
        networks = ', '.join([n.value for n in subscription.networks])
        
        status_message = f"""
📊 **Subscription Status**

Status: {'✅ Active' if subscription.active else '❌ Inactive'}
Tier: {subscription.tier.upper()}
Min Risk Level: {subscription.min_risk_level.value.upper()}
Watched Assets: {watched}
Networks: {networks}
Subscribed: {subscription.created_at.strftime('%Y-%m-%d')}

Modify settings: /settings
        """
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def watch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /watch command."""
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text(
                "Usage: /watch <symbol>\nExample: /watch BTC"
            )
            return
        
        symbol = context.args[0].upper()
        key = f"telegram_{user_id}"
        subscription = self.alert_manager.subscribers.get(key)
        
        if not subscription:
            await update.message.reply_text(
                "Please subscribe first: /subscribe"
            )
            return
        
        if symbol not in subscription.watched_assets:
            subscription.watched_assets.append(symbol)
            await update.message.reply_text(
                f"✅ Now watching {symbol}"
            )
        else:
            await update.message.reply_text(
                f"{symbol} is already in your watchlist"
            )
    
    async def unwatch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unwatch command."""
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text(
                "Usage: /unwatch <symbol>\nExample: /unwatch BTC"
            )
            return
        
        symbol = context.args[0].upper()
        key = f"telegram_{user_id}"
        subscription = self.alert_manager.subscribers.get(key)
        
        if not subscription:
            await update.message.reply_text(
                "Please subscribe first: /subscribe"
            )
            return
        
        if symbol in subscription.watched_assets:
            subscription.watched_assets.remove(symbol)
            await update.message.reply_text(
                f"❌ Stopped watching {symbol}"
            )
        else:
            await update.message.reply_text(
                f"{symbol} is not in your watchlist"
            )
    
    async def risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /risk command."""
        if not context.args:
            await update.message.reply_text(
                "Usage: /risk <symbol>\nExample: /risk BTC"
            )
            return
        
        symbol = context.args[0].upper()
        
        # In production, fetch actual risk assessment
        await update.message.reply_text(
            f"⏳ Analyzing risk for {symbol}...\n\n"
            "This feature requires the full system to be running.\n"
            "Subscribe to get automatic alerts: /subscribe"
        )
    
    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command."""
        settings_message = """
⚙️ **Alert Settings**

To change your settings, use these commands:

**Risk Level:**
/setlevel low - Get all alerts
/setlevel medium - Medium and above (default)
/setlevel high - Only high and critical
/setlevel critical - Only critical

**Networks:**
/networks - View/change network preferences

**Watchlist:**
/watch <symbol> - Add to watchlist
/unwatch <symbol> - Remove from watchlist
/listwatch - Show watchlist

Current status: /status
        """
        
        await update.message.reply_text(settings_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
🆘 **Crypto Risk Alert Bot - Help**

**Main Commands:**
/start - Welcome message
/subscribe - Start receiving alerts
/unsubscribe - Stop alerts
/status - Check subscription

**Monitoring:**
/watch <symbol> - Watch specific crypto
/unwatch <symbol> - Stop watching
/risk <symbol> - Get risk assessment

**Settings:**
/settings - Configure preferences
/setlevel <level> - Set min risk level
/networks - Manage networks

**Examples:**
/watch ETH
/risk BTC
/setlevel high

Need help? Contact @cryptorisksupport
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def send_alert_to_user(self, alert: Alert, chat_id: str):
        """Send alert to a specific user."""
        try:
            # Format alert message
            message = self._format_alert_message(alert)
            
            # Send message
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"Sent alert to Telegram chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def _format_alert_message(self, alert: Alert) -> str:
        """Format alert for Telegram."""
        return alert.message
    
    async def start_bot(self):
        """Start the Telegram bot."""
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return
        
        # Create application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe))
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(CommandHandler("watch", self.watch))
        self.application.add_handler(CommandHandler("unwatch", self.unwatch))
        self.application.add_handler(CommandHandler("risk", self.risk))
        self.application.add_handler(CommandHandler("settings", self.settings))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Start bot
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Telegram bot is running!")


async def main():
    """Main entry point for running the Telegram bot standalone."""
    import yaml
    
    # Load config
    with open('config/config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create alert manager
    alert_manager = AlertManager(config)
    
    # Create and start bot
    bot = TelegramBot(config, alert_manager)
    await bot.start_bot()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Telegram bot...")


if __name__ == '__main__':
    asyncio.run(main())
