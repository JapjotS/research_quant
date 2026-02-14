"""
RVOL Detector - Relative Volume Spike Detection

Detects volume spikes that are 3x-5x higher than the 10-day average.
A surge almost always begins with such a volume spike.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class RVOLDetector:
    """
    Detects Relative Volume (RVOL) spikes that often precede
    stock surges.
    """
    
    def __init__(
        self,
        ibkr_connector,
        avg_period_days: int = 10,
        spike_threshold: float = 3.0
    ):
        """
        Initialize RVOL Detector
        
        Args:
            ibkr_connector: IBKRConnector instance
            avg_period_days: Period for calculating average volume
            spike_threshold: Minimum multiplier for volume spike (default 3x)
        """
        self.ibkr = ibkr_connector
        self.avg_period_days = avg_period_days
        self.spike_threshold = spike_threshold
        self.logger = logger
        
        self.logger.info(
            f"RVOL Detector initialized "
            f"(avg_period={avg_period_days}d, threshold={spike_threshold}x)"
        )
        
        # Cache for historical volumes
        self.volume_cache = {}
        
    def calculate_rvol(
        self,
        symbol: str,
        current_volume: Optional[int] = None
    ) -> Dict:
        """
        Calculate Relative Volume for a symbol
        
        Args:
            symbol: Stock ticker
            current_volume: Current volume (if None, fetches from IBKR)
            
        Returns:
            Dictionary with RVOL metrics
        """
        # Get current volume if not provided
        if current_volume is None:
            market_data = self.ibkr.get_market_data(symbol)
            current_volume = market_data.get('volume', 0)
        
        # Get historical average
        avg_volume = self._get_average_volume(symbol)
        
        if avg_volume == 0:
            rvol = 0
        else:
            rvol = current_volume / avg_volume
        
        return {
            'symbol': symbol,
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'rvol': rvol,
            'is_spike': rvol >= self.spike_threshold,
            'timestamp': datetime.now()
        }
    
    def _get_average_volume(self, symbol: str) -> float:
        """
        Get average volume for the symbol
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Average volume over the period
        """
        # Check cache first
        if symbol in self.volume_cache:
            cached = self.volume_cache[symbol]
            # Cache valid for 1 hour
            if (datetime.now() - cached['timestamp']).seconds < 3600:
                return cached['avg_volume']
        
        # Fetch historical data from IBKR
        historical = self.ibkr.get_historical_data(
            symbol,
            duration=f'{self.avg_period_days} D',
            bar_size='1 day'
        )
        
        if not historical:
            self.logger.warning(f"No historical data for {symbol}")
            return 0
        
        # Calculate average
        volumes = [bar['volume'] for bar in historical]
        avg_volume = np.mean(volumes)
        
        # Cache the result
        self.volume_cache[symbol] = {
            'avg_volume': avg_volume,
            'timestamp': datetime.now()
        }
        
        return avg_volume
    
    def scan_for_volume_spikes(
        self,
        symbols: List[str],
        min_threshold: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Scan multiple symbols for volume spikes
        
        Args:
            symbols: List of symbols to scan
            min_threshold: Override default spike threshold
            
        Returns:
            DataFrame with stocks showing volume spikes
        """
        if min_threshold is None:
            min_threshold = self.spike_threshold
        
        self.logger.info(
            f"Scanning {len(symbols)} symbols for volume spikes "
            f"(threshold: {min_threshold}x)"
        )
        
        results = []
        for symbol in symbols:
            try:
                rvol_data = self.calculate_rvol(symbol)
                if rvol_data['rvol'] >= min_threshold:
                    results.append(rvol_data)
            except Exception as e:
                self.logger.error(f"Error scanning {symbol}: {e}")
        
        df = pd.DataFrame(results)
        
        if not df.empty:
            df = df.sort_values('rvol', ascending=False)
            self.logger.info(
                f"Found {len(df)} stocks with volume spikes >= {min_threshold}x"
            )
        
        return df
    
    def get_intraday_rvol(
        self,
        symbol: str,
        time_of_day: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate intraday RVOL (comparing to typical volume at this time)
        
        Args:
            symbol: Stock ticker
            time_of_day: Time to compare (default: now)
            
        Returns:
            Dictionary with intraday RVOL metrics
        """
        if time_of_day is None:
            time_of_day = datetime.now()
        
        # In production, this would compare current intraday volume
        # to typical volume at this time of day
        
        # Get current market data
        market_data = self.ibkr.get_market_data(symbol)
        current_volume = market_data.get('volume', 0)
        
        # Estimate typical volume at this time
        # (In production, use historical intraday patterns)
        avg_daily_volume = self._get_average_volume(symbol)
        
        # Rough estimate: distribute volume throughout trading day
        # Assuming more volume in first/last hour
        hour = time_of_day.hour
        if 9 <= hour < 10 or 15 <= hour < 16:
            expected_pct = 0.20  # 20% in opening/closing hours
        else:
            expected_pct = 0.60 / 6  # 60% distributed over 6 middle hours
        
        expected_volume = avg_daily_volume * expected_pct
        
        intraday_rvol = current_volume / expected_volume if expected_volume > 0 else 0
        
        return {
            'symbol': symbol,
            'current_volume': current_volume,
            'expected_volume': expected_volume,
            'intraday_rvol': intraday_rvol,
            'time': time_of_day,
            'is_unusual': intraday_rvol >= 2.0  # 2x for intraday
        }
    
    def monitor_realtime_rvol(
        self,
        symbols: List[str],
        callback: Optional[callable] = None,
        check_interval: int = 60
    ):
        """
        Monitor RVOL in real-time for a watchlist
        
        Args:
            symbols: Symbols to monitor
            callback: Function to call when spike detected
            check_interval: Seconds between checks
        """
        self.logger.info(
            f"Starting real-time RVOL monitoring for {len(symbols)} symbols"
        )
        
        # In production, this would run continuously
        # For demonstration, we'll do a single check
        
        spikes = self.scan_for_volume_spikes(symbols)
        
        if not spikes.empty:
            self.logger.info(f"Detected {len(spikes)} volume spikes")
            
            if callback:
                for _, row in spikes.iterrows():
                    callback(row.to_dict())
        else:
            self.logger.info("No volume spikes detected")
        
        return spikes
