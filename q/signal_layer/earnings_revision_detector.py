"""
Earnings Revision Detector

Detects stocks where analyst consensus estimates are trending upward
before earnings dates. Surges often happen when the market is "behind"
the analyst revisions.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class EarningsRevisionDetector:
    """
    Monitors analyst earnings revisions to identify stocks with
    upward estimate momentum before earnings announcements.
    """
    
    def __init__(self, api_credentials: Optional[Dict[str, str]] = None):
        """
        Initialize the Earnings Revision Detector
        
        Args:
            api_credentials: Capital IQ API credentials
        """
        self.api_credentials = api_credentials
        self.logger = logger
        self.logger.info("Earnings Revision Detector initialized")
        
    def detect_positive_revisions(
        self,
        symbols: List[str],
        lookback_days: int = 30,
        min_revision_count: int = 3
    ) -> pd.DataFrame:
        """
        Detect stocks with positive earnings revisions
        
        Args:
            symbols: List of stock symbols to analyze
            lookback_days: Number of days to look back for revisions
            min_revision_count: Minimum number of revisions required
            
        Returns:
            DataFrame with stocks showing positive revision trends
        """
        self.logger.info(f"Detecting earnings revisions for {len(symbols)} stocks")
        
        results = []
        for symbol in symbols:
            try:
                revision_data = self._analyze_revisions(
                    symbol, 
                    lookback_days,
                    min_revision_count
                )
                if revision_data:
                    results.append(revision_data)
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
                
        df = pd.DataFrame(results)
        
        if not df.empty:
            df = df.sort_values('revision_momentum', ascending=False)
            self.logger.info(f"Found {len(df)} stocks with positive revisions")
        
        return df
    
    def _analyze_revisions(
        self,
        symbol: str,
        lookback_days: int,
        min_revision_count: int
    ) -> Optional[Dict]:
        """
        Analyze earnings revisions for a single stock
        
        Args:
            symbol: Stock ticker
            lookback_days: Lookback period
            min_revision_count: Minimum revisions required
            
        Returns:
            Dictionary with revision analysis or None
        """
        # In production, this would query Capital IQ API
        # Example API call structure:
        """
        from spgmiciq import CIQClient
        
        if self.api_credentials:
            client = CIQClient(**self.api_credentials)
            
            # Get analyst consensus estimates over time
            estimates = client.get_consensus_estimates(
                symbol=symbol,
                start_date=datetime.now() - timedelta(days=lookback_days),
                estimate_type='EPS'
            )
            
            # Get individual analyst revisions
            revisions = client.get_analyst_revisions(
                symbol=symbol,
                lookback_days=lookback_days
            )
            
            # Calculate revision metrics
            revision_momentum = self._calculate_revision_momentum(estimates, revisions)
        """
        
        # Simulated revision analysis for demonstration
        import random
        
        revision_count = random.randint(0, 10)
        if revision_count < min_revision_count:
            return None
            
        # Simulate positive revision trend
        upward_revisions = random.randint(revision_count // 2, revision_count)
        downward_revisions = revision_count - upward_revisions
        
        if upward_revisions <= downward_revisions:
            return None
        
        # Calculate metrics
        revision_momentum = (upward_revisions - downward_revisions) / revision_count * 100
        avg_revision_magnitude = random.uniform(0.5, 5.0)  # % change
        
        # Get next earnings date (simulated)
        days_to_earnings = random.randint(1, 90)
        next_earnings_date = datetime.now() + timedelta(days=days_to_earnings)
        
        return {
            'symbol': symbol,
            'revision_momentum': revision_momentum,
            'upward_revisions': upward_revisions,
            'downward_revisions': downward_revisions,
            'total_revisions': revision_count,
            'avg_revision_magnitude': avg_revision_magnitude,
            'next_earnings_date': next_earnings_date,
            'days_to_earnings': days_to_earnings,
            'detected_at': datetime.now()
        }
    
    def _calculate_revision_momentum(
        self,
        estimates: pd.DataFrame,
        revisions: List[Dict]
    ) -> float:
        """
        Calculate earnings revision momentum score
        
        Args:
            estimates: Time series of consensus estimates
            revisions: List of individual analyst revisions
            
        Returns:
            Momentum score (0-100)
        """
        if estimates.empty or not revisions:
            return 0.0
        
        # Calculate trend in consensus estimates
        estimates_sorted = estimates.sort_values('date')
        estimate_values = estimates_sorted['eps_estimate'].values
        
        # Linear regression on estimate trend
        x = np.arange(len(estimate_values))
        if len(estimate_values) > 1:
            slope, _ = np.polyfit(x, estimate_values, 1)
            trend_score = max(0, min(slope * 100, 100))
        else:
            trend_score = 0
        
        # Calculate revision ratio (up vs down)
        up_count = sum(1 for r in revisions if r.get('direction') == 'up')
        down_count = sum(1 for r in revisions if r.get('direction') == 'down')
        total = up_count + down_count
        
        if total > 0:
            revision_ratio_score = (up_count / total) * 100
        else:
            revision_ratio_score = 0
        
        # Weighted average
        momentum = 0.6 * revision_ratio_score + 0.4 * trend_score
        
        return momentum
    
    def get_pre_earnings_candidates(
        self,
        symbols: List[str],
        days_ahead: int = 30,
        min_momentum: float = 60.0
    ) -> List[str]:
        """
        Get stocks with positive revisions ahead of earnings
        
        Args:
            symbols: Symbols to analyze
            days_ahead: Only include stocks with earnings in next N days
            min_momentum: Minimum revision momentum score
            
        Returns:
            List of candidate symbols
        """
        results = self.detect_positive_revisions(symbols)
        
        if results.empty:
            return []
        
        # Filter by earnings date and momentum
        filtered = results[
            (results['days_to_earnings'] <= days_ahead) &
            (results['revision_momentum'] >= min_momentum)
        ]
        
        candidates = filtered['symbol'].tolist()
        
        self.logger.info(
            f"Found {len(candidates)} pre-earnings candidates "
            f"(earnings within {days_ahead} days, momentum >= {min_momentum})"
        )
        
        return candidates
