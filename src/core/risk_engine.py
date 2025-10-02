"""Risk scoring engine with explainability."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import numpy as np
from src.models.schemas import (
    RiskAssessment, RiskLevel, WhaleTransfer, 
    ContractRisk, SentimentData, Network
)

logger = logging.getLogger(__name__)


class RiskEngine:
    """Main risk scoring engine with explainable AI."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.weights = config.get('risk_scoring', {}).get('weights', {
            'whale_transfer': 0.3,
            'contract_analysis': 0.4,
            'sentiment': 0.3
        })
        self.thresholds = config.get('risk_scoring', {}).get('thresholds', {
            'critical': 8.0,
            'high': 6.0,
            'medium': 4.0,
            'low': 2.0
        })
    
    def calculate_whale_risk(
        self, 
        transfers: List[WhaleTransfer],
        time_window_hours: int = 24
    ) -> Tuple[float, List[str]]:
        """Calculate risk score based on whale transfers."""
        if not transfers:
            return 0.0, []
        
        recent_transfers = [
            t for t in transfers 
            if t.timestamp > datetime.now() - timedelta(hours=time_window_hours)
        ]
        
        if not recent_transfers:
            return 0.0, []
        
        # Calculate risk factors
        total_value = sum(t.usd_value for t in recent_transfers)
        avg_value = total_value / len(recent_transfers)
        max_value = max(t.usd_value for t in recent_transfers)
        
        # Check for exchange dumps
        exchange_transfers = [t for t in recent_transfers if t.is_exchange]
        exchange_ratio = len(exchange_transfers) / len(recent_transfers) if recent_transfers else 0
        
        # Risk calculation
        value_score = min(total_value / 10_000_000, 5.0)  # Max 5 points for value
        frequency_score = min(len(recent_transfers) / 10, 3.0)  # Max 3 points for frequency
        exchange_score = exchange_ratio * 2.0  # Max 2 points for exchange dumps
        
        whale_risk = value_score + frequency_score + exchange_score
        
        # Generate explanations
        explanations = []
        if total_value > 5_000_000:
            explanations.append(f"High transfer volume: ${total_value:,.0f} in 24h")
        if len(recent_transfers) > 5:
            explanations.append(f"Frequent transfers: {len(recent_transfers)} in 24h")
        if exchange_ratio > 0.5:
            explanations.append(f"High exchange activity: {len(exchange_transfers)} exchange transfers")
        if max_value > 2_000_000:
            explanations.append(f"Large single transfer: ${max_value:,.0f}")
        
        return min(whale_risk, 10.0), explanations
    
    def calculate_contract_risk(
        self, 
        contract_analysis: ContractRisk
    ) -> Tuple[float, List[str]]:
        """Calculate risk score based on contract analysis."""
        if not contract_analysis:
            return 0.0, []
        
        explanations = []
        risk_score = contract_analysis.risk_score
        
        if contract_analysis.has_hidden_owner:
            explanations.append("Hidden or renounced ownership detected")
        if contract_analysis.has_unlimited_mint:
            explanations.append("Unlimited minting capability found")
        if not contract_analysis.liquidity_locked:
            explanations.append("Liquidity is not locked - rug pull risk")
        if contract_analysis.honeypot_risk:
            explanations.append("Honeypot indicators detected")
        if contract_analysis.owner_can_pause:
            explanations.append("Owner can pause trading")
        
        return risk_score, explanations
    
    def calculate_sentiment_risk(
        self, 
        sentiment_data: List[SentimentData],
        time_window_hours: int = 6
    ) -> Tuple[float, List[str]]:
        """Calculate risk score based on sentiment analysis."""
        if not sentiment_data:
            return 0.0, []
        
        recent_sentiment = [
            s for s in sentiment_data 
            if s.timestamp > datetime.now() - timedelta(hours=time_window_hours)
        ]
        
        if not recent_sentiment:
            return 0.0, []
        
        # Calculate weighted sentiment score
        total_volume = sum(s.volume for s in recent_sentiment)
        weighted_sentiment = sum(
            s.sentiment_score * s.volume for s in recent_sentiment
        ) / total_volume if total_volume > 0 else 0
        
        # Convert sentiment to risk (negative sentiment = higher risk)
        sentiment_risk = (1 - weighted_sentiment) * 5  # Scale -1 to 1 -> 0 to 10
        
        explanations = []
        if weighted_sentiment < -0.3:
            explanations.append(f"Very negative sentiment: {weighted_sentiment:.2f}")
        elif weighted_sentiment < 0:
            explanations.append(f"Negative sentiment: {weighted_sentiment:.2f}")
        
        # Check for trending negative sentiment
        trending_negative = any(
            s.trending and s.sentiment_score < -0.2 
            for s in recent_sentiment
        )
        if trending_negative:
            explanations.append("Trending with negative sentiment")
            sentiment_risk += 2.0
        
        # Check volume spike
        avg_volume = total_volume / len(recent_sentiment)
        if avg_volume > 1000:
            explanations.append(f"High discussion volume: {int(avg_volume)} mentions/platform")
        
        return min(sentiment_risk, 10.0), explanations
    
    def assess_risk(
        self,
        asset_symbol: str,
        whale_transfers: List[WhaleTransfer] = None,
        contract_analysis: ContractRisk = None,
        sentiment_data: List[SentimentData] = None,
        network: Network = None,
        contract_address: str = None
    ) -> RiskAssessment:
        """Generate comprehensive risk assessment with explanations."""
        
        whale_transfers = whale_transfers or []
        sentiment_data = sentiment_data or []
        
        # Calculate component risks
        whale_risk, whale_explanations = self.calculate_whale_risk(whale_transfers)
        contract_risk, contract_explanations = self.calculate_contract_risk(contract_analysis)
        sentiment_risk, sentiment_explanations = self.calculate_sentiment_risk(sentiment_data)
        
        # Calculate weighted overall risk
        overall_risk = (
            whale_risk * self.weights['whale_transfer'] +
            contract_risk * self.weights['contract_analysis'] +
            sentiment_risk * self.weights['sentiment']
        )
        
        # Determine risk level
        risk_level = self._get_risk_level(overall_risk)
        
        # Combine all explanations
        all_explanations = whale_explanations + contract_explanations + sentiment_explanations
        
        # Generate overall explanation
        explanation = self._generate_explanation(
            overall_risk, risk_level, 
            whale_risk, contract_risk, sentiment_risk,
            all_explanations
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, contract_analysis, whale_transfers, sentiment_data
        )
        
        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(
            whale_transfers, contract_analysis, sentiment_data
        )
        
        return RiskAssessment(
            asset_symbol=asset_symbol,
            contract_address=contract_address,
            network=network,
            overall_risk_score=round(overall_risk, 2),
            risk_level=risk_level,
            whale_risk_score=round(whale_risk, 2),
            contract_risk_score=round(contract_risk, 2),
            sentiment_risk_score=round(sentiment_risk, 2),
            whale_transfers=whale_transfers[:10],  # Limit to recent 10
            contract_analysis=contract_analysis,
            sentiment_data=sentiment_data[:5],  # Limit to recent 5
            explanation=explanation,
            risk_factors=all_explanations,
            recommendations=recommendations,
            timestamp=datetime.now(),
            confidence=confidence
        )
    
    def _get_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= self.thresholds['critical']:
            return RiskLevel.CRITICAL
        elif score >= self.thresholds['high']:
            return RiskLevel.HIGH
        elif score >= self.thresholds['medium']:
            return RiskLevel.MEDIUM
        elif score >= self.thresholds['low']:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE
    
    def _generate_explanation(
        self, 
        overall_risk: float, 
        risk_level: RiskLevel,
        whale_risk: float,
        contract_risk: float,
        sentiment_risk: float,
        factors: List[str]
    ) -> str:
        """Generate human-readable explanation of risk assessment."""
        
        explanation = f"Risk Level: {risk_level.value.upper()} ({overall_risk:.1f}/10)\n\n"
        
        # Component breakdown
        explanation += "Risk Components:\n"
        explanation += f"• Whale Activity: {whale_risk:.1f}/10\n"
        explanation += f"• Contract Security: {contract_risk:.1f}/10\n"
        explanation += f"• Market Sentiment: {sentiment_risk:.1f}/10\n\n"
        
        # Main factors
        if factors:
            explanation += "Key Risk Factors:\n"
            for factor in factors[:5]:  # Top 5 factors
                explanation += f"• {factor}\n"
        
        return explanation
    
    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        contract_analysis: ContractRisk,
        whale_transfers: List[WhaleTransfer],
        sentiment_data: List[SentimentData]
    ) -> List[str]:
        """Generate actionable recommendations based on risk assessment."""
        
        recommendations = []
        
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            recommendations.append("⚠️ Consider exiting position or reducing exposure")
            recommendations.append("Do not enter new positions at this time")
        
        if contract_analysis:
            if not contract_analysis.liquidity_locked:
                recommendations.append("Verify liquidity lock before investing")
            if contract_analysis.has_unlimited_mint:
                recommendations.append("Unlimited mint capability - high dilution risk")
            if contract_analysis.honeypot_risk:
                recommendations.append("Possible honeypot - verify you can sell tokens")
        
        if whale_transfers:
            recent_exchange_dumps = [
                t for t in whale_transfers 
                if t.is_exchange and t.timestamp > datetime.now() - timedelta(hours=24)
            ]
            if len(recent_exchange_dumps) > 3:
                recommendations.append("Multiple whale dumps to exchanges detected")
        
        if sentiment_data:
            avg_sentiment = np.mean([s.sentiment_score for s in sentiment_data])
            if avg_sentiment < -0.5:
                recommendations.append("Very negative market sentiment - wait for stabilization")
        
        if risk_level == RiskLevel.SAFE:
            recommendations.append("Risk appears manageable with current data")
            recommendations.append("Continue monitoring for changes")
        
        return recommendations
    
    def _calculate_confidence(
        self,
        whale_transfers: List[WhaleTransfer],
        contract_analysis: ContractRisk,
        sentiment_data: List[SentimentData]
    ) -> float:
        """Calculate confidence score based on data availability."""
        
        confidence_factors = []
        
        # Data availability
        if whale_transfers:
            confidence_factors.append(0.3)
        if contract_analysis:
            confidence_factors.append(0.4)
        if sentiment_data:
            confidence_factors.append(0.3)
        
        # Data recency (last 24 hours)
        if whale_transfers:
            recent = [t for t in whale_transfers 
                     if t.timestamp > datetime.now() - timedelta(hours=24)]
            if recent:
                confidence_factors.append(0.1)
        
        if sentiment_data:
            recent = [s for s in sentiment_data 
                     if s.timestamp > datetime.now() - timedelta(hours=24)]
            if recent:
                confidence_factors.append(0.1)
        
        return min(sum(confidence_factors), 1.0)
