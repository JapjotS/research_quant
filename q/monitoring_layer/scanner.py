"""
Surge Scanner - Main Scanner Logic

Combines signals from multiple sources to detect stocks
about to surge. Implements the core scanner logic:

IF (CapIQ Sentiment == Positive) 
AND (Current Volume > 200% of Avg) 
AND (Price > 20-day EMA) 
THEN (Execute Buy)
"""

import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SurgeScanner:
    """
    Main surge detection scanner that combines:
    - Capital IQ signals (fundamentals)
    - RVOL spikes (volume)
    - Order book imbalances (momentum)
    - Price action (technical)
    """
    
    def __init__(
        self,
        ibkr_connector,
        rvol_detector,
        order_book_analyzer,
        min_catalyst_score: float = 60.0,
        min_rvol: float = 2.0,
        min_imbalance: float = 1.5
    ):
        """
        Initialize Surge Scanner
        
        Args:
            ibkr_connector: IBKRConnector instance
            rvol_detector: RVOLDetector instance
            order_book_analyzer: OrderBookAnalyzer instance
            min_catalyst_score: Minimum Capital IQ catalyst score
            min_rvol: Minimum relative volume ratio
            min_imbalance: Minimum order book imbalance ratio
        """
        self.ibkr = ibkr_connector
        self.rvol_detector = rvol_detector
        self.order_book = order_book_analyzer
        
        self.min_catalyst_score = min_catalyst_score
        self.min_rvol = min_rvol
        self.min_imbalance = min_imbalance
        
        self.logger = logger
        self.logger.info("Surge Scanner initialized")
        
    def scan_symbol(
        self,
        symbol: str,
        catalyst_score: Optional[float] = None
    ) -> Dict:
        """
        Scan a single symbol for surge potential
        
        Args:
            symbol: Stock ticker
            catalyst_score: Pre-calculated catalyst score from Capital IQ
            
        Returns:
            Dictionary with scan results
        """
        try:
            # Get market data
            market_data = self.ibkr.get_market_data(symbol)
            current_price = market_data.get('last', 0)
            
            # Calculate RVOL
            rvol_data = self.rvol_detector.calculate_rvol(symbol)
            rvol = rvol_data['rvol']
            
            # Analyze order book
            order_book_data = self.order_book.analyze_order_book(symbol)
            imbalance = order_book_data.get('imbalance_ratio', 1.0)
            
            # Calculate 20-day EMA
            ema_20 = self._calculate_ema(symbol, period=20)
            price_above_ema = current_price > ema_20 if ema_20 > 0 else False
            
            # Apply scanner logic
            signals = {
                'catalyst': catalyst_score and catalyst_score >= self.min_catalyst_score,
                'volume': rvol >= self.min_rvol,
                'order_book': imbalance >= self.min_imbalance,
                'price_action': price_above_ema
            }
            
            # Count positive signals
            signal_count = sum(1 for s in signals.values() if s)
            
            # Calculate composite score (0-100)
            composite_score = 0
            if signals['catalyst']:
                composite_score += 30
            if signals['volume']:
                composite_score += 25
            if signals['order_book']:
                composite_score += 25
            if signals['price_action']:
                composite_score += 20
            
            # Determine recommendation
            if signal_count >= 3 and composite_score >= 75:
                recommendation = 'STRONG_BUY'
            elif signal_count >= 2 and composite_score >= 50:
                recommendation = 'BUY'
            elif signal_count >= 1:
                recommendation = 'WATCH'
            else:
                recommendation = 'PASS'
            
            return {
                'symbol': symbol,
                'price': current_price,
                'ema_20': ema_20,
                'rvol': rvol,
                'imbalance_ratio': imbalance,
                'catalyst_score': catalyst_score,
                'signals': signals,
                'signal_count': signal_count,
                'composite_score': composite_score,
                'recommendation': recommendation,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error scanning {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'recommendation': 'ERROR'
            }
    
    def scan_watchlist(
        self,
        watchlist: List[str],
        catalyst_scores: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Scan entire watchlist for surge candidates
        
        Args:
            watchlist: List of symbols to scan
            catalyst_scores: Optional dict mapping symbols to catalyst scores
            
        Returns:
            DataFrame with scan results, sorted by composite score
        """
        self.logger.info(f"Scanning watchlist of {len(watchlist)} stocks")
        
        results = []
        for symbol in watchlist:
            catalyst_score = catalyst_scores.get(symbol) if catalyst_scores else None
            scan_result = self.scan_symbol(symbol, catalyst_score)
            
            if 'error' not in scan_result:
                results.append(scan_result)
        
        df = pd.DataFrame(results)
        
        if not df.empty:
            df = df.sort_values('composite_score', ascending=False)
            
            # Filter to actionable stocks
            actionable = df[df['recommendation'].isin(['BUY', 'STRONG_BUY'])]
            
            self.logger.info(
                f"Scan complete: {len(actionable)} actionable opportunities "
                f"out of {len(df)} stocks"
            )
        
        return df
    
    def _calculate_ema(
        self,
        symbol: str,
        period: int = 20
    ) -> float:
        """
        Calculate Exponential Moving Average
        
        Args:
            symbol: Stock ticker
            period: EMA period
            
        Returns:
            EMA value
        """
        # Get historical data
        historical = self.ibkr.get_historical_data(
            symbol,
            duration=f'{period * 2} D',  # Get extra data for accuracy
            bar_size='1 day'
        )
        
        if not historical or len(historical) < period:
            self.logger.warning(f"Insufficient data for EMA calculation: {symbol}")
            return 0
        
        # Extract close prices
        closes = [bar['close'] for bar in historical]
        
        # Calculate EMA
        ema = self._ema_calc(closes, period)
        
        return ema
    
    @staticmethod
    def _ema_calc(data: List[float], period: int) -> float:
        """Calculate EMA using standard formula"""
        if len(data) < period:
            return 0
        
        # Start with SMA
        sma = np.mean(data[:period])
        
        # EMA multiplier
        multiplier = 2 / (period + 1)
        
        # Calculate EMA
        ema = sma
        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def execute_buy_signal(
        self,
        symbol: str,
        quantity: int,
        order_type: str = 'MKT',
        dry_run: bool = True
    ) -> Dict:
        """
        Execute buy order for a surge candidate
        
        Args:
            symbol: Stock ticker
            quantity: Number of shares
            order_type: Order type ('MKT', 'LMT')
            dry_run: If True, log only without executing
            
        Returns:
            Order result dictionary
        """
        if dry_run:
            self.logger.info(
                f"DRY RUN: Would BUY {quantity} shares of {symbol} ({order_type})"
            )
            return {
                'symbol': symbol,
                'action': 'BUY',
                'quantity': quantity,
                'order_type': order_type,
                'status': 'DRY_RUN',
                'timestamp': datetime.now()
            }
        
        # Execute actual order
        result = self.ibkr.place_order(
            symbol=symbol,
            action='BUY',
            quantity=quantity,
            order_type=order_type
        )
        
        self.logger.info(
            f"EXECUTED: BUY {quantity} shares of {symbol} - "
            f"Order ID: {result.get('order_id')}, Status: {result.get('status')}"
        )
        
        return result
    
    def run_continuous_scan(
        self,
        watchlist: List[str],
        catalyst_scores: Optional[Dict[str, float]] = None,
        callback: Optional[Callable] = None,
        scan_interval: int = 60
    ):
        """
        Run continuous scanning of watchlist
        
        Args:
            watchlist: Symbols to monitor
            catalyst_scores: Catalyst scores from Capital IQ
            callback: Function to call when opportunities found
            scan_interval: Seconds between scans
        """
        self.logger.info("="*70)
        self.logger.info("STARTING CONTINUOUS SURGE SCANNER")
        self.logger.info("="*70)
        self.logger.info(f"Watchlist: {len(watchlist)} stocks")
        self.logger.info(f"Scan interval: {scan_interval} seconds")
        
        # In production, this would run in a loop
        # For demonstration, run one scan
        
        results = self.scan_watchlist(watchlist, catalyst_scores)
        
        if not results.empty:
            # Get actionable opportunities
            opportunities = results[
                results['recommendation'].isin(['BUY', 'STRONG_BUY'])
            ]
            
            if not opportunities.empty:
                self.logger.info(f"\n{'='*70}")
                self.logger.info("SURGE OPPORTUNITIES DETECTED")
                self.logger.info(f"{'='*70}\n")
                
                for _, opp in opportunities.iterrows():
                    self.logger.info(
                        f"{opp['symbol']}: {opp['recommendation']} "
                        f"(Score: {opp['composite_score']:.0f}, "
                        f"RVOL: {opp['rvol']:.1f}x, "
                        f"Signals: {opp['signal_count']}/4)"
                    )
                    
                    if callback:
                        callback(opp.to_dict())
            else:
                self.logger.info("No surge opportunities at this time")
        
        return results
    
    def get_summary_statistics(self, scan_results: pd.DataFrame) -> Dict:
        """
        Get summary statistics from scan results
        
        Args:
            scan_results: DataFrame from scan_watchlist
            
        Returns:
            Dictionary with summary stats
        """
        if scan_results.empty:
            return {'error': 'No scan results'}
        
        return {
            'total_scanned': len(scan_results),
            'strong_buy': len(scan_results[scan_results['recommendation'] == 'STRONG_BUY']),
            'buy': len(scan_results[scan_results['recommendation'] == 'BUY']),
            'watch': len(scan_results[scan_results['recommendation'] == 'WATCH']),
            'pass': len(scan_results[scan_results['recommendation'] == 'PASS']),
            'avg_composite_score': scan_results['composite_score'].mean(),
            'avg_rvol': scan_results['rvol'].mean(),
            'avg_imbalance': scan_results['imbalance_ratio'].mean(),
            'top_opportunities': scan_results.head(5)[['symbol', 'composite_score', 'recommendation']].to_dict('records')
        }
