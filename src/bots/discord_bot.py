"""Discord bot for delivering crypto risk alerts."""

import logging
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from src.models.schemas import UserSubscription, RiskLevel, Network, Alert
from src.core.alert_manager import AlertManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for crypto risk alerts."""
    
    def __init__(self, config: dict, alert_manager: AlertManager):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.config = config
        self.alert_manager = alert_manager
        self.bot_token = config.get('alerts', {}).get('discord', {}).get('bot_token')
        
        # Register commands
        self.setup_commands()
    
    def setup_commands(self):
        """Set up bot commands."""
        
        @self.command(name='start')
        async def start(ctx):
            """Show welcome message."""
            embed = discord.Embed(
                title="🚀 Crypto Risk Alert Bot",
                description="Monitor cryptocurrency risks in real-time!",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Features",
                value="• 🐋 Whale wallet transfers\n"
                      "• 🔒 Smart contract vulnerabilities\n"
                      "• 📊 Social sentiment analysis",
                inline=False
            )
            
            embed.add_field(
                name="Commands",
                value="!subscribe - Subscribe to alerts\n"
                      "!status - Check subscription\n"
                      "!watch <symbol> - Watch a crypto\n"
                      "!risk <symbol> - Get risk assessment\n"
                      "!help - Show all commands",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='subscribe')
        async def subscribe(ctx):
            """Subscribe to alerts."""
            user_id = str(ctx.author.id)
            chat_id = str(ctx.channel.id)
            
            subscription = UserSubscription(
                user_id=user_id,
                platform='discord',
                chat_id=chat_id,
                min_risk_level=RiskLevel.MEDIUM,
                watched_assets=[],
                networks=[Network.ETHEREUM],
                active=True,
                created_at=datetime.now(),
                tier='free'
            )
            
            self.alert_manager.add_subscriber(subscription)
            
            embed = discord.Embed(
                title="✅ Subscribed Successfully",
                description="You will now receive crypto risk alerts!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Default Settings",
                value="• Risk Level: MEDIUM and above\n"
                      "• Networks: Ethereum\n"
                      "• Assets: All (use !watch to focus)",
                inline=False
            )
            
            embed.add_field(
                name="Next Steps",
                value="Configure preferences: !settings\n"
                      "Watch specific crypto: !watch BTC",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='unsubscribe')
        async def unsubscribe(ctx):
            """Unsubscribe from alerts."""
            user_id = str(ctx.author.id)
            self.alert_manager.remove_subscriber('discord', user_id)
            
            await ctx.send("❌ You have been unsubscribed from alerts.")
        
        @self.command(name='status')
        async def status(ctx):
            """Check subscription status."""
            user_id = str(ctx.author.id)
            key = f"discord_{user_id}"
            subscription = self.alert_manager.subscribers.get(key)
            
            if not subscription:
                await ctx.send("You are not subscribed. Use !subscribe to get started.")
                return
            
            watched = ', '.join(subscription.watched_assets) if subscription.watched_assets else 'All'
            networks = ', '.join([n.value for n in subscription.networks])
            
            embed = discord.Embed(
                title="📊 Subscription Status",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Status", value="✅ Active" if subscription.active else "❌ Inactive", inline=True)
            embed.add_field(name="Tier", value=subscription.tier.upper(), inline=True)
            embed.add_field(name="Min Risk Level", value=subscription.min_risk_level.value.upper(), inline=True)
            embed.add_field(name="Watched Assets", value=watched, inline=False)
            embed.add_field(name="Networks", value=networks, inline=False)
            embed.add_field(name="Subscribed", value=subscription.created_at.strftime('%Y-%m-%d'), inline=True)
            
            await ctx.send(embed=embed)
        
        @self.command(name='watch')
        async def watch(ctx, symbol: str = None):
            """Watch a specific crypto."""
            if not symbol:
                await ctx.send("Usage: !watch <symbol>\nExample: !watch BTC")
                return
            
            user_id = str(ctx.author.id)
            symbol = symbol.upper()
            key = f"discord_{user_id}"
            subscription = self.alert_manager.subscribers.get(key)
            
            if not subscription:
                await ctx.send("Please subscribe first: !subscribe")
                return
            
            if symbol not in subscription.watched_assets:
                subscription.watched_assets.append(symbol)
                await ctx.send(f"✅ Now watching {symbol}")
            else:
                await ctx.send(f"{symbol} is already in your watchlist")
        
        @self.command(name='unwatch')
        async def unwatch(ctx, symbol: str = None):
            """Stop watching a crypto."""
            if not symbol:
                await ctx.send("Usage: !unwatch <symbol>\nExample: !unwatch BTC")
                return
            
            user_id = str(ctx.author.id)
            symbol = symbol.upper()
            key = f"discord_{user_id}"
            subscription = self.alert_manager.subscribers.get(key)
            
            if not subscription:
                await ctx.send("Please subscribe first: !subscribe")
                return
            
            if symbol in subscription.watched_assets:
                subscription.watched_assets.remove(symbol)
                await ctx.send(f"❌ Stopped watching {symbol}")
            else:
                await ctx.send(f"{symbol} is not in your watchlist")
        
        @self.command(name='risk')
        async def risk(ctx, symbol: str = None):
            """Get risk assessment for a crypto."""
            if not symbol:
                await ctx.send("Usage: !risk <symbol>\nExample: !risk BTC")
                return
            
            symbol = symbol.upper()
            
            embed = discord.Embed(
                title=f"⏳ Analyzing {symbol}",
                description="Risk analysis in progress...\n\n"
                           "This feature requires the full system to be running.\n"
                           "Subscribe to get automatic alerts: !subscribe",
                color=discord.Color.orange()
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='settings')
        async def settings(ctx):
            """Show settings options."""
            embed = discord.Embed(
                title="⚙️ Alert Settings",
                description="Configure your alert preferences",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Risk Level",
                value="!setlevel low - All alerts\n"
                      "!setlevel medium - Medium+ (default)\n"
                      "!setlevel high - High+ only\n"
                      "!setlevel critical - Critical only",
                inline=False
            )
            
            embed.add_field(
                name="Watchlist",
                value="!watch <symbol> - Add to watchlist\n"
                      "!unwatch <symbol> - Remove\n"
                      "!listwatch - Show watchlist",
                inline=False
            )
            
            embed.add_field(
                name="Status",
                value="!status - View current settings",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.command(name='help')
        async def help_command(ctx):
            """Show help message."""
            embed = discord.Embed(
                title="🆘 Help - Crypto Risk Alert Bot",
                description="Available commands and usage",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Main Commands",
                value="!start - Welcome message\n"
                      "!subscribe - Start receiving alerts\n"
                      "!unsubscribe - Stop alerts\n"
                      "!status - Check subscription",
                inline=False
            )
            
            embed.add_field(
                name="Monitoring",
                value="!watch <symbol> - Watch specific crypto\n"
                      "!unwatch <symbol> - Stop watching\n"
                      "!risk <symbol> - Get risk assessment",
                inline=False
            )
            
            embed.add_field(
                name="Settings",
                value="!settings - Configure preferences\n"
                      "!setlevel <level> - Set min risk level",
                inline=False
            )
            
            embed.add_field(
                name="Examples",
                value="!watch ETH\n"
                      "!risk BTC\n"
                      "!setlevel high",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    async def send_alert_to_channel(self, alert: Alert, channel_id: str):
        """Send alert to a specific Discord channel."""
        try:
            channel = self.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Channel {channel_id} not found")
                return False
            
            embed = self._create_alert_embed(alert)
            await channel.send(embed=embed)
            
            logger.info(f"Sent alert to Discord channel {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False
    
    def _create_alert_embed(self, alert: Alert) -> discord.Embed:
        """Create Discord embed for alert."""
        
        color_map = {
            RiskLevel.CRITICAL: discord.Color.red(),
            RiskLevel.HIGH: discord.Color.orange(),
            RiskLevel.MEDIUM: discord.Color.gold(),
            RiskLevel.LOW: discord.Color.blue(),
            RiskLevel.SAFE: discord.Color.green()
        }
        
        embed = discord.Embed(
            title=alert.title,
            description=alert.message[:2000],  # Discord limit
            color=color_map.get(alert.risk_level, discord.Color.blue()),
            timestamp=alert.timestamp
        )
        
        embed.add_field(
            name="Risk Score",
            value=f"{alert.risk_assessment.overall_risk_score}/10",
            inline=True
        )
        
        embed.add_field(
            name="Risk Level",
            value=alert.risk_level.value.upper(),
            inline=True
        )
        
        if alert.contract_address:
            embed.add_field(
                name="Contract",
                value=f"`{alert.contract_address[:10]}...`",
                inline=True
            )
        
        return embed
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'Discord bot logged in as {self.user}')
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="crypto risks | !help"
            )
        )
    
    def run_bot(self):
        """Run the Discord bot."""
        if not self.bot_token:
            logger.error("Discord bot token not configured")
            return
        
        logger.info("Starting Discord bot...")
        self.run(self.bot_token)


async def main():
    """Main entry point for running the Discord bot standalone."""
    import yaml
    
    # Load config
    with open('config/config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create alert manager
    alert_manager = AlertManager(config)
    
    # Create and start bot
    bot = DiscordBot(config, alert_manager)
    bot.run_bot()


if __name__ == '__main__':
    asyncio.run(main())
