"""Social sentiment analyzer for crypto assets."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
import aiohttp
import re
from src.models.schemas import SentimentData

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze social sentiment from Twitter, Reddit, and other platforms."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.sentiment_config = config.get('sentiment', {})
        self.platforms = self.sentiment_config.get('scraping', {}).get('platforms', [])
    
    async def analyze_sentiment(
        self, 
        symbol: str,
        hours_back: int = 24
    ) -> List[SentimentData]:
        """Analyze sentiment for a crypto asset across platforms."""
        
        sentiment_data = []
        
        # Fetch from each enabled platform
        if 'twitter' in self.platforms:
            twitter_sentiment = await self._analyze_twitter(symbol, hours_back)
            if twitter_sentiment:
                sentiment_data.append(twitter_sentiment)
        
        if 'reddit' in self.platforms:
            reddit_sentiment = await self._analyze_reddit(symbol, hours_back)
            if reddit_sentiment:
                sentiment_data.append(reddit_sentiment)
        
        if 'telegram_channels' in self.platforms:
            telegram_sentiment = await self._analyze_telegram(symbol, hours_back)
            if telegram_sentiment:
                sentiment_data.append(telegram_sentiment)
        
        return sentiment_data
    
    async def _analyze_twitter(self, symbol: str, hours_back: int) -> SentimentData:
        """Analyze Twitter sentiment for a symbol."""
        
        # In production, use Twitter API v2 with tweepy
        # For MVP, this is a simplified implementation
        
        try:
            # Fetch tweets (in production, use real Twitter API)
            tweets = await self._fetch_twitter_data(symbol, hours_back)
            
            if not tweets:
                return None
            
            # Analyze sentiment using simple keyword analysis
            # In production, use transformer models like FinBERT
            sentiment_score = self._calculate_sentiment_score(tweets)
            
            # Check if trending
            trending = len(tweets) > 500  # Simple threshold
            
            # Extract keywords
            keywords = self._extract_keywords(tweets)
            
            return SentimentData(
                symbol=symbol,
                platform='twitter',
                sentiment_score=sentiment_score,
                volume=len(tweets),
                trending=trending,
                keywords=keywords[:10],
                timestamp=datetime.now(),
                sample_texts=tweets[:5]
            )
        except Exception as e:
            logger.error(f"Error analyzing Twitter sentiment: {e}")
            return None
    
    async def _analyze_reddit(self, symbol: str, hours_back: int) -> SentimentData:
        """Analyze Reddit sentiment for a symbol."""
        
        try:
            # Fetch Reddit posts and comments
            posts = await self._fetch_reddit_data(symbol, hours_back)
            
            if not posts:
                return None
            
            # Analyze sentiment
            sentiment_score = self._calculate_sentiment_score(posts)
            
            # Check engagement
            trending = len(posts) > 100
            
            # Extract keywords
            keywords = self._extract_keywords(posts)
            
            return SentimentData(
                symbol=symbol,
                platform='reddit',
                sentiment_score=sentiment_score,
                volume=len(posts),
                trending=trending,
                keywords=keywords[:10],
                timestamp=datetime.now(),
                sample_texts=posts[:5]
            )
        except Exception as e:
            logger.error(f"Error analyzing Reddit sentiment: {e}")
            return None
    
    async def _analyze_telegram(self, symbol: str, hours_back: int) -> SentimentData:
        """Analyze Telegram channel sentiment."""
        
        try:
            # In production, scrape Telegram channels or use Telegram API
            messages = await self._fetch_telegram_data(symbol, hours_back)
            
            if not messages:
                return None
            
            sentiment_score = self._calculate_sentiment_score(messages)
            keywords = self._extract_keywords(messages)
            
            return SentimentData(
                symbol=symbol,
                platform='telegram',
                sentiment_score=sentiment_score,
                volume=len(messages),
                trending=len(messages) > 200,
                keywords=keywords[:10],
                timestamp=datetime.now(),
                sample_texts=messages[:5]
            )
        except Exception as e:
            logger.error(f"Error analyzing Telegram sentiment: {e}")
            return None
    
    async def _fetch_twitter_data(self, symbol: str, hours_back: int) -> List[str]:
        """Fetch Twitter data for a symbol."""
        
        # In production, use Twitter API v2
        # This is a mock implementation
        
        twitter_config = self.sentiment_config.get('twitter', {})
        bearer_token = twitter_config.get('bearer_token')
        
        if not bearer_token:
            logger.warning("Twitter bearer token not configured")
            return []
        
        # Mock data for demonstration
        # In production, implement actual Twitter API calls
        mock_tweets = [
            f"${symbol} looking bullish! Great project! 🚀",
            f"Not sure about ${symbol}, seems risky",
            f"${symbol} to the moon! Best crypto ever!",
            f"Warning: ${symbol} might be a scam",
            f"Just bought more ${symbol}, feeling good",
        ]
        
        return mock_tweets
    
    async def _fetch_reddit_data(self, symbol: str, hours_back: int) -> List[str]:
        """Fetch Reddit data for a symbol."""
        
        # In production, use PRAW (Python Reddit API Wrapper)
        reddit_config = self.sentiment_config.get('reddit', {})
        client_id = reddit_config.get('client_id')
        
        if not client_id:
            logger.warning("Reddit client ID not configured")
            return []
        
        # Mock data
        mock_posts = [
            f"Analysis: {symbol} fundamentals look strong",
            f"PSA: {symbol} contract has some red flags",
            f"{symbol} partnership announcement coming soon!",
            f"Sold all my {symbol}, not worth the risk",
            f"{symbol} community is amazing, HODL!",
        ]
        
        return mock_posts
    
    async def _fetch_telegram_data(self, symbol: str, hours_back: int) -> List[str]:
        """Fetch Telegram data for a symbol."""
        
        # In production, use Telegram API or scraping
        # Mock implementation
        mock_messages = [
            f"{symbol} team delivered on roadmap!",
            f"Warning about {symbol} liquidity",
            f"{symbol} price action looking good",
            f"Be careful with {symbol}, do your research",
            f"{symbol} is the future of DeFi!",
        ]
        
        return mock_messages
    
    def _calculate_sentiment_score(self, texts: List[str]) -> float:
        """Calculate sentiment score from texts using keyword analysis."""
        
        # In production, use transformer models like FinBERT, VADER, or TextBlob
        # This is a simplified keyword-based approach
        
        positive_keywords = [
            'bullish', 'moon', 'buy', 'pump', 'great', 'amazing', 'best',
            'strong', 'good', 'partnership', 'launch', 'success', 'profit',
            'gem', 'undervalued', 'hold', 'hodl', 'trust', 'solid'
        ]
        
        negative_keywords = [
            'bearish', 'dump', 'sell', 'scam', 'rug', 'red flag', 'warning',
            'risky', 'bad', 'avoid', 'crash', 'loss', 'fraud', 'honeypot',
            'suspicious', 'careful', 'danger', 'exit', 'liquidate'
        ]
        
        positive_count = 0
        negative_count = 0
        
        for text in texts:
            text_lower = text.lower()
            
            for keyword in positive_keywords:
                if keyword in text_lower:
                    positive_count += 1
            
            for keyword in negative_keywords:
                if keyword in text_lower:
                    negative_count += 1
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return 0.0
        
        # Normalize to -1 to 1 range
        sentiment = (positive_count - negative_count) / total_count
        
        return max(-1.0, min(1.0, sentiment))
    
    def _extract_keywords(self, texts: List[str]) -> List[str]:
        """Extract important keywords from texts."""
        
        # Simple keyword extraction
        # In production, use TF-IDF or more sophisticated NLP
        
        word_freq = {}
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        for text in texts:
            # Clean and tokenize
            words = re.findall(r'\b\w+\b', text.lower())
            
            for word in words:
                if word not in stop_words and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_keywords[:20]]
    
    async def monitor_continuous(self, symbols: List[str], callback):
        """Continuously monitor sentiment for given symbols."""
        
        logger.info(f"Starting continuous sentiment monitoring for {len(symbols)} symbols")
        
        update_interval = self.sentiment_config.get('scraping', {}).get('update_interval', 300)
        
        while True:
            try:
                for symbol in symbols:
                    sentiment_data = await self.analyze_sentiment(symbol, hours_back=6)
                    
                    if sentiment_data:
                        logger.info(f"Analyzed sentiment for {symbol}: {len(sentiment_data)} platforms")
                        await callback(symbol, sentiment_data)
                
                # Wait before next check
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"Error in continuous sentiment monitoring: {e}")
                await asyncio.sleep(60)
