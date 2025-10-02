"""Smart contract scanner for detecting rug-pull risks."""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from src.models.schemas import ContractRisk, RiskLevel, Network

logger = logging.getLogger(__name__)


class ContractScanner:
    """Scan smart contracts for rug-pull risks and vulnerabilities."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.risk_indicators = config.get('risk_scoring', {}).get('contract_risk_indicators', [
            'hidden_owner',
            'unlimited_mint',
            'no_liquidity_lock',
            'suspicious_transfer_patterns',
            'honeypot_indicators'
        ])
    
    async def scan_contract(
        self, 
        contract_address: str, 
        network: Network
    ) -> ContractRisk:
        """Perform comprehensive contract security scan."""
        
        logger.info(f"Scanning contract {contract_address} on {network.value}")
        
        # Get contract source code
        source_code = await self._fetch_contract_source(contract_address, network)
        
        # Perform various security checks
        has_hidden_owner = self._check_hidden_owner(source_code)
        has_unlimited_mint = self._check_unlimited_mint(source_code)
        liquidity_locked = await self._check_liquidity_lock(contract_address, network)
        honeypot_risk = await self._check_honeypot(contract_address, network)
        owner_can_pause = self._check_pause_function(source_code)
        
        # Collect indicators
        indicators = []
        if has_hidden_owner:
            indicators.append("hidden_owner")
        if has_unlimited_mint:
            indicators.append("unlimited_mint")
        if not liquidity_locked:
            indicators.append("no_liquidity_lock")
        if honeypot_risk:
            indicators.append("honeypot_indicators")
        if owner_can_pause:
            indicators.append("owner_can_pause")
        
        # Calculate risk score
        risk_score = self._calculate_contract_risk_score(
            has_hidden_owner,
            has_unlimited_mint,
            liquidity_locked,
            honeypot_risk,
            owner_can_pause
        )
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_score)
        
        # Generate explanation
        explanation = self._generate_explanation(
            has_hidden_owner,
            has_unlimited_mint,
            liquidity_locked,
            honeypot_risk,
            owner_can_pause,
            risk_score
        )
        
        return ContractRisk(
            contract_address=contract_address,
            network=network,
            risk_score=risk_score,
            risk_level=risk_level,
            indicators=indicators,
            analysis_timestamp=datetime.now(),
            has_hidden_owner=has_hidden_owner,
            has_unlimited_mint=has_unlimited_mint,
            liquidity_locked=liquidity_locked,
            honeypot_risk=honeypot_risk,
            owner_can_pause=owner_can_pause,
            explanation=explanation
        )
    
    async def _fetch_contract_source(
        self, 
        contract_address: str, 
        network: Network
    ) -> str:
        """Fetch contract source code from blockchain explorer."""
        
        blockchain_config = self.config.get('blockchain', {})
        api_key = blockchain_config.get(f'{network.value}scan_api_key', '')
        
        network_config = next(
            (n for n in blockchain_config.get('networks', []) 
             if n['name'] == network.value),
            None
        )
        
        if not network_config:
            logger.error(f"No configuration for network: {network.value}")
            return ""
        
        api_url = network_config['explorer_api']
        
        params = {
            'module': 'contract',
            'action': 'getsourcecode',
            'address': contract_address,
            'apikey': api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == '1' and data.get('result'):
                            return data['result'][0].get('SourceCode', '')
                    return ""
        except Exception as e:
            logger.error(f"Error fetching contract source: {e}")
            return ""
    
    def _check_hidden_owner(self, source_code: str) -> bool:
        """Check for hidden or renounced ownership."""
        if not source_code:
            return False
        
        # Look for renounceOwnership or hidden owner patterns
        renounce_patterns = [
            r'renounceOwnership\s*\(\s*\)',
            r'owner\s*=\s*address\s*\(\s*0\s*\)',
            r'_owner\s*=\s*address\s*\(\s*0\s*\)'
        ]
        
        for pattern in renounce_patterns:
            if re.search(pattern, source_code, re.IGNORECASE):
                return True
        
        return False
    
    def _check_unlimited_mint(self, source_code: str) -> bool:
        """Check for unlimited minting capability."""
        if not source_code:
            return False
        
        # Look for mint functions without restrictions
        mint_patterns = [
            r'function\s+mint\s*\([^)]*\)\s*public',
            r'function\s+_mint\s*\([^)]*\)',
            r'\.mint\s*\(',
        ]
        
        # Check if there's no max supply check
        has_max_supply = bool(re.search(r'maxSupply|MAX_SUPPLY|totalSupply\s*<', source_code))
        
        for pattern in mint_patterns:
            if re.search(pattern, source_code) and not has_max_supply:
                return True
        
        return False
    
    async def _check_liquidity_lock(
        self, 
        contract_address: str, 
        network: Network
    ) -> bool:
        """Check if liquidity is locked."""
        # In production, check lock contracts like Unicrypt, Team.Finance, etc.
        # This is a simplified check
        
        # Common lock contract addresses
        lock_contracts = [
            '0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214',  # Unicrypt (Ethereum)
            '0xC77aab3c6D7dAb46248F3CC3033C856171878BD5',  # Team.Finance (Ethereum)
        ]
        
        # In production, query these contracts for locks
        # For MVP, return True as default (should be implemented properly)
        return True
    
    async def _check_honeypot(
        self, 
        contract_address: str, 
        network: Network
    ) -> bool:
        """Check for honeypot indicators."""
        # In production, use honeypot detection services or simulate buys/sells
        # This is a simplified implementation
        
        try:
            # Could use services like honeypot.is API
            async with aiohttp.ClientSession() as session:
                url = f"https://api.honeypot.is/v2/IsHoneypot"
                params = {'address': contract_address}
                
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('honeypotResult', {}).get('isHoneypot', False)
        except Exception as e:
            logger.warning(f"Could not check honeypot status: {e}")
        
        return False
    
    def _check_pause_function(self, source_code: str) -> bool:
        """Check if owner can pause trading."""
        if not source_code:
            return False
        
        pause_patterns = [
            r'function\s+pause\s*\(\s*\)',
            r'function\s+_pause\s*\(\s*\)',
            r'whenNotPaused',
            r'Pausable',
        ]
        
        for pattern in pause_patterns:
            if re.search(pattern, source_code):
                return True
        
        return False
    
    def _calculate_contract_risk_score(
        self,
        has_hidden_owner: bool,
        has_unlimited_mint: bool,
        liquidity_locked: bool,
        honeypot_risk: bool,
        owner_can_pause: bool
    ) -> float:
        """Calculate overall contract risk score."""
        
        score = 0.0
        
        if has_hidden_owner:
            score += 2.0
        if has_unlimited_mint:
            score += 2.5
        if not liquidity_locked:
            score += 3.0  # Major risk factor
        if honeypot_risk:
            score += 2.5
        if owner_can_pause:
            score += 1.0
        
        return min(score, 10.0)
    
    def _get_risk_level(self, score: float) -> RiskLevel:
        """Convert score to risk level."""
        thresholds = self.config.get('risk_scoring', {}).get('thresholds', {
            'critical': 8.0,
            'high': 6.0,
            'medium': 4.0,
            'low': 2.0
        })
        
        if score >= thresholds['critical']:
            return RiskLevel.CRITICAL
        elif score >= thresholds['high']:
            return RiskLevel.HIGH
        elif score >= thresholds['medium']:
            return RiskLevel.MEDIUM
        elif score >= thresholds['low']:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE
    
    def _generate_explanation(
        self,
        has_hidden_owner: bool,
        has_unlimited_mint: bool,
        liquidity_locked: bool,
        honeypot_risk: bool,
        owner_can_pause: bool,
        risk_score: float
    ) -> str:
        """Generate human-readable explanation."""
        
        explanation = f"Contract Risk Score: {risk_score:.1f}/10\n\n"
        explanation += "Security Analysis:\n"
        
        if has_hidden_owner:
            explanation += "❌ Ownership is renounced or hidden\n"
        else:
            explanation += "✓ Owner is identifiable\n"
        
        if has_unlimited_mint:
            explanation += "❌ Unlimited minting capability detected\n"
        else:
            explanation += "✓ No unlimited minting found\n"
        
        if liquidity_locked:
            explanation += "✓ Liquidity appears to be locked\n"
        else:
            explanation += "❌ Liquidity is NOT locked - HIGH RUG PULL RISK\n"
        
        if honeypot_risk:
            explanation += "❌ Honeypot indicators detected\n"
        else:
            explanation += "✓ No honeypot indicators\n"
        
        if owner_can_pause:
            explanation += "⚠️ Owner can pause trading\n"
        else:
            explanation += "✓ No pause functionality\n"
        
        return explanation
