"""
Order Book Analyzer - Level II Data Analysis

Analyzes order book imbalances using IBKR Level II data.
Massive buy interest (bids stacking) with thin asks signals
an imminent breakout.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class OrderBookAnalyzer:
    """
    Analyzes Level II market data to detect order book imbalances
    that precede price breakouts.
    """
    
    def __init__(
        self,
        ibkr_connector,
        imbalance_threshold: float = 2.0
    ):
        """
        Initialize Order Book Analyzer
        
        Args:
            ibkr_connector: IBKRConnector instance
            imbalance_threshold: Minimum bid/ask imbalance ratio
        """
        self.ibkr = ibkr_connector
        self.imbalance_threshold = imbalance_threshold
        self.logger = logger
        
        self.logger.info(
            f"Order Book Analyzer initialized "
            f"(imbalance_threshold={imbalance_threshold})"
        )
        
    def analyze_order_book(self, symbol: str) -> Dict:
        """
        Analyze order book for a symbol
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Dictionary with order book analysis
        """
        # Get Level II data from IBKR
        level2 = self.ibkr.get_level2_data(symbol)
        
        if not level2:
            return {'error': 'No Level II data available'}
        
        bids = level2.get('bids', [])
        asks = level2.get('asks', [])
        
        # Calculate bid and ask volumes
        bid_volume = sum(bid['size'] for bid in bids)
        ask_volume = sum(ask['size'] for ask in asks)
        
        # Calculate imbalance ratio
        if ask_volume > 0:
            imbalance_ratio = bid_volume / ask_volume
        else:
            imbalance_ratio = float('inf') if bid_volume > 0 else 1.0
        
        # Determine imbalance direction
        if imbalance_ratio > self.imbalance_threshold:
            direction = 'BUY_PRESSURE'
            strength = (imbalance_ratio - 1.0) / self.imbalance_threshold
        elif imbalance_ratio < (1.0 / self.imbalance_threshold):
            direction = 'SELL_PRESSURE'
            strength = (1.0 - imbalance_ratio) / (1.0 / self.imbalance_threshold)
        else:
            direction = 'BALANCED'
            strength = 0.0
        
        # Calculate bid-ask spread
        if bids and asks:
            best_bid = bids[0]['price']
            best_ask = asks[0]['price']
            spread = best_ask - best_bid
            spread_pct = (spread / best_bid) * 100 if best_bid > 0 else 0
        else:
            spread = 0
            spread_pct = 0
        
        return {
            'symbol': symbol,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume,
            'imbalance_ratio': imbalance_ratio,
            'direction': direction,
            'strength': strength,
            'spread': spread,
            'spread_pct': spread_pct,
            'bids_count': len(bids),
            'asks_count': len(asks),
            'timestamp': level2.get('timestamp', datetime.now())
        }
    
    def detect_breakout_setup(self, symbol: str) -> Dict:
        """
        Detect if order book shows breakout setup
        (heavy bid stacking with thin asks)
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Dictionary with breakout analysis
        """
        analysis = self.analyze_order_book(symbol)
        
        if 'error' in analysis:
            return analysis
        
        # Breakout criteria:
        # 1. Strong buy pressure (imbalance_ratio > threshold)
        # 2. Tight spread (< 0.1%)
        # 3. Multiple bid levels stacking up
        
        is_breakout_setup = (
            analysis['direction'] == 'BUY_PRESSURE' and
            analysis['imbalance_ratio'] >= self.imbalance_threshold and
            analysis['spread_pct'] < 0.1 and
            analysis['bids_count'] >= 5
        )
        
        # Calculate confidence score
        if is_breakout_setup:
            confidence = min(100, (
                (analysis['imbalance_ratio'] / self.imbalance_threshold) * 50 +
                (1.0 - min(analysis['spread_pct'], 0.1) / 0.1) * 25 +
                min(analysis['bids_count'] / 10, 1.0) * 25
            ))
        else:
            confidence = 0
        
        return {
            **analysis,
            'is_breakout_setup': is_breakout_setup,
            'confidence': confidence,
            'recommendation': 'STRONG_BUY' if confidence > 75 else 
                            'BUY' if confidence > 50 else 
                            'WATCH' if confidence > 25 else 'PASS'
        }
    
    def scan_for_imbalances(
        self,
        symbols: List[str],
        direction: Optional[str] = 'BUY_PRESSURE'
    ) -> pd.DataFrame:
        """
        Scan multiple symbols for order book imbalances
        
        Args:
            symbols: List of symbols to scan
            direction: Filter by direction ('BUY_PRESSURE', 'SELL_PRESSURE', or None for all)
            
        Returns:
            DataFrame with symbols showing imbalances
        """
        self.logger.info(
            f"Scanning {len(symbols)} symbols for order book imbalances"
        )
        
        results = []
        for symbol in symbols:
            try:
                analysis = self.analyze_order_book(symbol)
                
                if 'error' not in analysis:
                    # Filter by direction if specified
                    if direction is None or analysis['direction'] == direction:
                        if abs(analysis['imbalance_ratio'] - 1.0) > 0.5:  # Significant imbalance
                            results.append(analysis)
                            
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
        
        df = pd.DataFrame(results)
        
        if not df.empty:
            df = df.sort_values('imbalance_ratio', ascending=False)
            self.logger.info(
                f"Found {len(df)} stocks with order book imbalances"
            )
        
        return df
    
    def get_order_flow_sentiment(self, symbol: str) -> Dict:
        """
        Get overall order flow sentiment from order book
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Dictionary with sentiment analysis
        """
        analysis = self.analyze_order_book(symbol)
        
        if 'error' in analysis:
            return analysis
        
        # Categorize sentiment based on imbalance
        imbalance = analysis['imbalance_ratio']
        
        if imbalance >= 3.0:
            sentiment = 'VERY_BULLISH'
            score = 90
        elif imbalance >= 2.0:
            sentiment = 'BULLISH'
            score = 70
        elif imbalance >= 1.5:
            sentiment = 'SLIGHTLY_BULLISH'
            score = 60
        elif imbalance <= 0.33:
            sentiment = 'VERY_BEARISH'
            score = 10
        elif imbalance <= 0.5:
            sentiment = 'BEARISH'
            score = 30
        elif imbalance <= 0.67:
            sentiment = 'SLIGHTLY_BEARISH'
            score = 40
        else:
            sentiment = 'NEUTRAL'
            score = 50
        
        return {
            'symbol': symbol,
            'sentiment': sentiment,
            'score': score,
            'imbalance_ratio': imbalance,
            'bid_volume': analysis['bid_volume'],
            'ask_volume': analysis['ask_volume'],
            'timestamp': analysis['timestamp']
        }
    
    def monitor_realtime_imbalances(
        self,
        symbols: List[str],
        callback: Optional[callable] = None
    ):
        """
        Monitor order book imbalances in real-time
        
        Args:
            symbols: Symbols to monitor
            callback: Function to call when significant imbalance detected
        """
        self.logger.info(
            f"Starting real-time order book monitoring for {len(symbols)} symbols"
        )
        
        # Scan for current imbalances
        imbalances = self.scan_for_imbalances(symbols, direction='BUY_PRESSURE')
        
        if not imbalances.empty:
            self.logger.info(
                f"Detected {len(imbalances)} order book imbalances"
            )
            
            if callback:
                for _, row in imbalances.iterrows():
                    callback(row.to_dict())
        
        return imbalances
