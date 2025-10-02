"""Blockchain monitoring service for whale wallet transfers."""

import logging
from datetime import datetime
from typing import List, Dict, Optional
import asyncio
import aiohttp
from web3 import Web3
from src.models.schemas import WhaleTransfer, Network

logger = logging.getLogger(__name__)


class BlockchainMonitor:
    """Monitor blockchain for whale wallet transfers."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.networks = self._init_networks()
        self.whale_thresholds = config.get('blockchain', {}).get('whale_thresholds', {})
        self.known_exchanges = self._load_exchange_addresses()
    
    def _init_networks(self) -> Dict[str, Web3]:
        """Initialize Web3 connections for each network."""
        networks = {}
        blockchain_config = self.config.get('blockchain', {})
        
        for network_config in blockchain_config.get('networks', []):
            if network_config.get('enabled'):
                name = network_config['name']
                rpc_url = network_config['rpc_url'].format(
                    infura_project_id=blockchain_config.get('infura_project_id', '')
                )
                try:
                    networks[name] = Web3(Web3.HTTPProvider(rpc_url))
                    logger.info(f"Connected to {name} network")
                except Exception as e:
                    logger.error(f"Failed to connect to {name}: {e}")
        
        return networks
    
    def _load_exchange_addresses(self) -> Dict[str, List[str]]:
        """Load known exchange wallet addresses."""
        # In production, load from database or external API
        return {
            'ethereum': [
                '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance
                '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549',  # Binance 2
                '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE',  # Binance 3
                '0xD551234Ae421e3BCBA99A0Da6d736074f22192FF',  # Binance 4
                '0x564286362092D8e7936f0549571a803B203aAceD',  # Binance 5
                '0x0681d8Db095565FE8A346fA0277bFfdE9C0eDBBF',  # Binance 6
                '0xfE9e8709d3215310075d67E3ed32A380CCf451C8',  # Binance 7
                '0x4E9ce36E442e55EcD9025B9a6E0D88485d628A67',  # Binance 8
                '0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8',  # Binance 9
                '0xF977814e90dA44bFA03b6295A0616a897441aceC',  # Binance 10
                '0x8B353021189375591723E7384262F45709A3C3dC',  # Kraken
                '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0',  # Kraken 2
                '0x0A869d79a7052C7f1b55a8EbAbBEa3420F0D1E13',  # Kraken 3
                '0xE853c56864A2ebe4576a807D26Fdc4A0adA51919',  # Kraken 4
                '0x6cc5f688a315f3dc28a7781717a9a798a59fda7b',  # OKEx
                '0x236f9f97e0E62388479bf9e5BA4889e46B0273C3',  # Huobi
                '0x46705dfff24256421a05d056c29e81bdc09723b8',  # Coinbase
            ]
        }
    
    async def get_whale_transfers(
        self, 
        network: Network,
        min_value_usd: float = None,
        hours_back: int = 24
    ) -> List[WhaleTransfer]:
        """Get recent whale transfers for a network."""
        
        min_value_usd = min_value_usd or self.whale_thresholds.get('usd_value', 1_000_000)
        
        # In production, use Etherscan/BSCScan API or events
        # For MVP, this is a simplified implementation
        transfers = await self._fetch_transfers_from_api(network, hours_back)
        
        whale_transfers = []
        for transfer in transfers:
            if transfer['usd_value'] >= min_value_usd:
                whale_transfer = WhaleTransfer(
                    tx_hash=transfer['tx_hash'],
                    network=network,
                    from_address=transfer['from'],
                    to_address=transfer['to'],
                    amount=transfer['amount'],
                    token_symbol=transfer['symbol'],
                    usd_value=transfer['usd_value'],
                    timestamp=transfer['timestamp'],
                    is_exchange=self._is_exchange_address(transfer['to'], network),
                    exchange_name=self._get_exchange_name(transfer['to'], network)
                )
                whale_transfers.append(whale_transfer)
        
        return whale_transfers
    
    async def _fetch_transfers_from_api(
        self, 
        network: Network, 
        hours_back: int
    ) -> List[Dict]:
        """Fetch transfers from blockchain explorer API."""
        
        blockchain_config = self.config.get('blockchain', {})
        api_key = blockchain_config.get(f'{network.value}scan_api_key', '')
        
        network_config = next(
            (n for n in blockchain_config.get('networks', []) 
             if n['name'] == network.value),
            None
        )
        
        if not network_config:
            logger.error(f"No configuration found for network: {network.value}")
            return []
        
        api_url = network_config['explorer_api']
        
        # Example API call for large transfers
        # In production, implement pagination and proper error handling
        params = {
            'module': 'account',
            'action': 'tokentx',
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc',
            'apikey': api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Parse and filter transfers
                        return self._parse_transfer_data(data, network)
                    else:
                        logger.error(f"API request failed with status {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching transfers: {e}")
            return []
    
    def _parse_transfer_data(self, data: Dict, network: Network) -> List[Dict]:
        """Parse transfer data from API response."""
        transfers = []
        
        # This is a simplified parser - in production, handle various API formats
        if data.get('status') == '1' and data.get('result'):
            for tx in data['result'][:100]:  # Limit to recent 100
                try:
                    transfer = {
                        'tx_hash': tx.get('hash'),
                        'from': tx.get('from'),
                        'to': tx.get('to'),
                        'amount': float(tx.get('value', 0)) / 10**int(tx.get('tokenDecimal', 18)),
                        'symbol': tx.get('tokenSymbol', 'UNKNOWN'),
                        'usd_value': self._estimate_usd_value(
                            float(tx.get('value', 0)) / 10**int(tx.get('tokenDecimal', 18)),
                            tx.get('tokenSymbol', 'UNKNOWN')
                        ),
                        'timestamp': datetime.fromtimestamp(int(tx.get('timeStamp', 0)))
                    }
                    transfers.append(transfer)
                except Exception as e:
                    logger.error(f"Error parsing transfer: {e}")
                    continue
        
        return transfers
    
    def _estimate_usd_value(self, amount: float, symbol: str) -> float:
        """Estimate USD value of transfer."""
        # In production, fetch real-time prices from CoinGecko/CoinMarketCap
        # This is a simplified price mapping
        price_map = {
            'ETH': 2000,
            'BNB': 300,
            'MATIC': 0.80,
            'USDT': 1,
            'USDC': 1,
            'DAI': 1,
        }
        
        return amount * price_map.get(symbol, 0)
    
    def _is_exchange_address(self, address: str, network: Network) -> bool:
        """Check if address belongs to a known exchange."""
        exchange_addresses = self.known_exchanges.get(network.value, [])
        return address.lower() in [addr.lower() for addr in exchange_addresses]
    
    def _get_exchange_name(self, address: str, network: Network) -> Optional[str]:
        """Get exchange name for a known exchange address."""
        # In production, maintain a proper mapping
        if self._is_exchange_address(address, network):
            # Simplified mapping
            binance_addrs = self.known_exchanges.get(network.value, [])[:10]
            if address.lower() in [addr.lower() for addr in binance_addrs]:
                return "Binance"
            elif address.lower() in [
                '0x8B353021189375591723E7384262F45709A3C3dC'.lower(),
                '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0'.lower(),
            ]:
                return "Kraken"
            else:
                return "Exchange"
        return None
    
    async def monitor_continuous(self, callback):
        """Continuously monitor for whale transfers."""
        logger.info("Starting continuous blockchain monitoring")
        
        while True:
            try:
                for network_name in self.networks.keys():
                    network = Network(network_name)
                    transfers = await self.get_whale_transfers(network, hours_back=1)
                    
                    if transfers:
                        logger.info(f"Found {len(transfers)} whale transfers on {network.value}")
                        await callback(transfers)
                
                # Wait before next check (30 seconds)
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
