"""Main orchestrator for Crypto Risk Alert system."""

import asyncio
import logging
import yaml
from datetime import datetime
from src.core.risk_engine import RiskEngine
from src.services.blockchain_monitor import BlockchainMonitor
from src.services.contract_scanner import ContractScanner
from src.services.sentiment_analyzer import SentimentAnalyzer
from src.core.alert_manager import AlertManager
from src.models.schemas import RiskLevel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CryptoRiskAlertSystem:
    """Main orchestrator for the Crypto Risk Alert system."""
    
    def __init__(self, config_path: str = 'config/config.yml'):
        """Initialize the system with configuration."""
        
        logger.info("Initializing Crypto Risk Alert System...")
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize core components
        self.risk_engine = RiskEngine(self.config)
        self.blockchain_monitor = BlockchainMonitor(self.config)
        self.contract_scanner = ContractScanner(self.config)
        self.sentiment_analyzer = SentimentAnalyzer(self.config)
        self.alert_manager = AlertManager(self.config)
        
        # Track monitored assets
        self.monitored_assets = set()
        
        logger.info("System initialized successfully")
    
    async def process_whale_transfers(self, transfers):
        """Process whale transfers and generate alerts."""
        
        for transfer in transfers:
            logger.info(f"Processing whale transfer: {transfer.usd_value:,.0f} USD")
            
            # Calculate risk assessment
            assessment = self.risk_engine.assess_risk(
                asset_symbol=transfer.token_symbol,
                whale_transfers=[transfer],
                network=transfer.network
            )
            
            # Create alert if risk is significant
            if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                alert = await self.alert_manager.create_alert(
                    alert_type='whale_transfer',
                    risk_assessment=assessment
                )
                
                # Send alert
                await self.alert_manager.send_alert(alert)
    
    async def process_sentiment_data(self, symbol, sentiment_data):
        """Process sentiment data and generate alerts."""
        
        logger.info(f"Processing sentiment for {symbol}")
        
        # Calculate risk assessment
        assessment = self.risk_engine.assess_risk(
            asset_symbol=symbol,
            sentiment_data=sentiment_data
        )
        
        # Create alert if sentiment is very negative
        avg_sentiment = sum(s.sentiment_score for s in sentiment_data) / len(sentiment_data)
        if avg_sentiment < -0.5 or assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alert = await self.alert_manager.create_alert(
                alert_type='sentiment_shift',
                risk_assessment=assessment
            )
            
            await self.alert_manager.send_alert(alert)
    
    async def scan_and_alert_contract(self, contract_address, network):
        """Scan a contract and alert on risks."""
        
        logger.info(f"Scanning contract: {contract_address}")
        
        # Scan contract
        contract_analysis = await self.contract_scanner.scan_contract(
            contract_address=contract_address,
            network=network
        )
        
        # Create risk assessment
        assessment = self.risk_engine.assess_risk(
            asset_symbol="UNKNOWN",  # Would need to fetch token symbol
            contract_analysis=contract_analysis,
            network=network,
            contract_address=contract_address
        )
        
        # Alert on high risk contracts
        if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alert = await self.alert_manager.create_alert(
                alert_type='contract_risk',
                risk_assessment=assessment
            )
            
            await self.alert_manager.send_alert(alert)
        
        return contract_analysis
    
    async def add_monitored_asset(self, symbol: str):
        """Add an asset to monitoring."""
        self.monitored_assets.add(symbol)
        logger.info(f"Now monitoring: {symbol}")
    
    async def start_monitoring(self):
        """Start all monitoring services."""
        
        logger.info("Starting monitoring services...")
        
        # Start blockchain monitoring
        asyncio.create_task(
            self.blockchain_monitor.monitor_continuous(
                self.process_whale_transfers
            )
        )
        
        # Start sentiment monitoring for tracked assets
        # In production, dynamically update based on user subscriptions
        default_assets = ['BTC', 'ETH', 'BNB', 'USDT', 'USDC']
        for asset in default_assets:
            self.monitored_assets.add(asset)
        
        asyncio.create_task(
            self.sentiment_analyzer.monitor_continuous(
                list(self.monitored_assets),
                self.process_sentiment_data
            )
        )
        
        logger.info("Monitoring services started")
    
    async def run(self):
        """Run the main system."""
        
        logger.info("=" * 60)
        logger.info("CRYPTO RISK ALERT SYSTEM")
        logger.info("=" * 60)
        
        # Start monitoring
        await self.start_monitoring()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down system...")


async def main():
    """Main entry point."""
    
    system = CryptoRiskAlertSystem('config/config.example.yml')
    await system.run()


if __name__ == '__main__':
    asyncio.run(main())
