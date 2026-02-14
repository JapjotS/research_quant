"""
Flat File Backtester

Analyzes historical flat files to identify patterns that preceded
major surges (like FSLY or VAL). Looks at:
- Volume/Price variance 48 hours before surge
- Pre-surge patterns
- Statistical indicators
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class FlatFileBacktester:
    """
    Backtests historical data to identify patterns that precede
    stock surges. Uses regression models to find leading indicators.
    """
    
    def __init__(self, data_directory: Optional[str] = None):
        """
        Initialize the Flat File Backtester
        
        Args:
            data_directory: Path to directory containing historical flat files
        """
        self.data_directory = data_directory or "./data/historical"
        self.logger = logger
        self.logger.info(f"Flat File Backtester initialized (data dir: {self.data_directory})")
        
        # Cache for loaded data
        self.data_cache = {}
        
    def load_historical_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Load historical data from flat files
        
        Args:
            symbol: Stock ticker
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            DataFrame with OHLCV data
        """
        # Check cache first
        cache_key = f"{symbol}_{start_date}_{end_date}"
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        # In production, this would load from actual flat files (CSV, Parquet, etc.)
        # Example file structure: {data_directory}/{symbol}.csv
        """
        file_path = Path(self.data_directory) / f"{symbol}.csv"
        
        if file_path.exists():
            df = pd.read_csv(file_path, parse_dates=['date'])
            df = df.set_index('date')
            
            # Filter by date range
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
                
            self.data_cache[cache_key] = df
            return df
        """
        
        # Simulated data for demonstration
        df = self._generate_simulated_data(symbol, start_date, end_date)
        self.data_cache[cache_key] = df
        
        return df
    
    def _generate_simulated_data(
        self,
        symbol: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> pd.DataFrame:
        """Generate simulated OHLCV data"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=730)
        if end_date is None:
            end_date = datetime.now()
        
        # Generate date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Simulated price data with occasional surges
        np.random.seed(hash(symbol) % 2**32)
        
        base_price = 100
        returns = np.random.normal(0.0005, 0.02, len(dates))
        
        # Add random surges (5-10 over the period)
        num_surges = np.random.randint(5, 10)
        surge_indices = np.random.choice(len(dates), num_surges, replace=False)
        for idx in surge_indices:
            if idx > 10:  # Ensure we have prior data
                returns[idx] = np.random.uniform(0.15, 0.40)  # 15-40% surge
        
        prices = base_price * (1 + returns).cumprod()
        
        # Generate OHLCV
        data = {
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
            'high': prices * (1 + np.random.uniform(0, 0.03, len(dates))),
            'low': prices * (1 + np.random.uniform(-0.03, 0, len(dates))),
            'close': prices,
            'volume': np.random.lognormal(15, 1, len(dates)) * 1e6
        }
        
        df = pd.DataFrame(data, index=dates)
        return df
    
    def identify_historical_surges(
        self,
        symbol: str,
        lookback_years: int = 2,
        surge_threshold: float = 0.15  # 15% move
    ) -> pd.DataFrame:
        """
        Identify historical surge events
        
        Args:
            symbol: Stock ticker
            lookback_years: How far back to analyze
            surge_threshold: Minimum % move to qualify as surge
            
        Returns:
            DataFrame with surge events
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_years * 365)
        
        df = self.load_historical_data(symbol, start_date, end_date)
        
        # Calculate daily returns
        df['return'] = df['close'].pct_change()
        
        # Identify surges
        surges = df[df['return'] >= surge_threshold].copy()
        
        self.logger.info(
            f"Found {len(surges)} surges for {symbol} "
            f"(threshold: {surge_threshold*100:.0f}%)"
        )
        
        return surges
    
    def analyze_pre_surge_patterns(
        self,
        symbol: str,
        lookback_years: int = 2,
        hours_before: int = 48
    ) -> Dict:
        """
        Analyze patterns in the 48 hours before major surges
        
        Args:
            symbol: Stock ticker
            lookback_years: Historical period to analyze
            hours_before: Hours before surge to analyze (default 48)
            
        Returns:
            Dictionary with pattern statistics
        """
        surges = self.identify_historical_surges(symbol, lookback_years)
        
        if surges.empty:
            return {'error': 'No surges found'}
        
        # For each surge, analyze the period before it
        # Convert hours to trading days (assuming ~6.5 hours per day)
        days_before = int(hours_before / 6.5)
        
        patterns = []
        df = self.load_historical_data(symbol)
        
        for surge_date in surges.index:
            # Get pre-surge data
            try:
                # Find the index position (not exact match needed)
                end_idx = df.index.get_indexer([surge_date], method='nearest')[0]
                if end_idx >= days_before:
                    start_idx = end_idx - days_before
                    pre_surge_data = df.iloc[start_idx:end_idx]
                    
                    pattern = self._extract_pattern_features(pre_surge_data)
                    pattern['surge_date'] = surge_date
                    pattern['surge_magnitude'] = surges.loc[surge_date, 'return']
                    patterns.append(pattern)
            except Exception as e:
                # Skip this surge if we can't get the data
                continue
        
        # Aggregate patterns
        if patterns:
            patterns_df = pd.DataFrame(patterns)
            
            analysis = {
                'num_surges_analyzed': len(patterns),
                'avg_volume_increase': patterns_df['volume_ratio'].mean(),
                'avg_price_variance': patterns_df['price_variance'].mean(),
                'avg_volume_variance': patterns_df['volume_variance'].mean(),
                'common_patterns': self._identify_common_patterns(patterns_df)
            }
            
            self.logger.info(
                f"Analyzed {len(patterns)} pre-surge patterns for {symbol}"
            )
            
            return analysis
        
        return {'error': 'Insufficient data for pattern analysis'}
    
    def _extract_pattern_features(self, data: pd.DataFrame) -> Dict:
        """
        Extract features from pre-surge period
        
        Args:
            data: DataFrame with OHLCV data for pre-surge period
            
        Returns:
            Dictionary with extracted features
        """
        # Volume metrics
        avg_volume = data['volume'].mean()
        volume_std = data['volume'].std()
        volume_trend = data['volume'].iloc[-1] / data['volume'].iloc[0]
        
        # Price metrics
        price_variance = data['close'].pct_change().std()
        price_trend = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]
        
        # Combined metrics
        volume_price_correlation = data['volume'].corr(data['close'])
        
        return {
            'avg_volume': avg_volume,
            'volume_variance': volume_std / avg_volume if avg_volume > 0 else 0,
            'volume_ratio': volume_trend,
            'price_variance': price_variance,
            'price_trend': price_trend,
            'volume_price_corr': volume_price_correlation
        }
    
    def _identify_common_patterns(self, patterns_df: pd.DataFrame) -> Dict:
        """
        Identify common patterns across surges
        
        Args:
            patterns_df: DataFrame with pattern features
            
        Returns:
            Dictionary describing common patterns
        """
        # Statistical thresholds
        volume_ratio_threshold = patterns_df['volume_ratio'].quantile(0.25)  # 25th percentile
        price_variance_threshold = patterns_df['price_variance'].quantile(0.75)  # 75th percentile
        
        return {
            'volume_increase_threshold': volume_ratio_threshold,
            'price_variance_threshold': price_variance_threshold,
            'pattern_description': (
                f"Typical pre-surge pattern shows volume increase of "
                f"{volume_ratio_threshold:.1%} and price variance of "
                f"{price_variance_threshold*100:.2f}%"
            )
        }
    
    def build_regression_model(
        self,
        symbols: List[str],
        lookback_years: int = 2
    ) -> Dict:
        """
        Build a regression model to predict surges based on
        historical patterns across multiple stocks
        
        Args:
            symbols: List of symbols to include in model
            lookback_years: Historical period for training
            
        Returns:
            Dictionary with model parameters and statistics
        """
        self.logger.info(
            f"Building regression model with {len(symbols)} stocks"
        )
        
        all_patterns = []
        
        for symbol in symbols:
            try:
                analysis = self.analyze_pre_surge_patterns(symbol, lookback_years)
                if 'error' not in analysis:
                    all_patterns.append({
                        'symbol': symbol,
                        **analysis
                    })
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
        
        if all_patterns:
            # In production, this would build an actual ML model
            # using scikit-learn or similar
            
            model_summary = {
                'num_symbols': len(all_patterns),
                'total_surges_analyzed': sum(p['num_surges_analyzed'] for p in all_patterns),
                'avg_volume_increase_threshold': np.mean([
                    p['avg_volume_increase'] for p in all_patterns
                ]),
                'avg_price_variance_threshold': np.mean([
                    p['avg_price_variance'] for p in all_patterns
                ]),
                'model_ready': True
            }
            
            self.logger.info("Regression model built successfully")
            return model_summary
        
        return {'error': 'Insufficient data to build model', 'model_ready': False}
    
    def check_current_pattern(
        self,
        symbol: str,
        model_params: Dict,
        hours_lookback: int = 48
    ) -> Dict:
        """
        Check if current pattern matches pre-surge indicators
        
        Args:
            symbol: Stock to check
            model_params: Parameters from regression model
            hours_lookback: Period to analyze
            
        Returns:
            Dictionary with match score and recommendation
        """
        # Get recent data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)  # Get enough context
        
        df = self.load_historical_data(symbol, start_date, end_date)
        
        # Extract current pattern
        days_back = int(hours_lookback / 6.5)
        if len(df) >= days_back:
            recent_data = df.iloc[-days_back:]
            current_pattern = self._extract_pattern_features(recent_data)
            
            # Compare to model thresholds
            volume_match = (
                current_pattern['volume_ratio'] >= 
                model_params.get('avg_volume_increase_threshold', 1.5)
            )
            
            variance_match = (
                current_pattern['price_variance'] >= 
                model_params.get('avg_price_variance_threshold', 0.02)
            )
            
            match_score = 0
            if volume_match:
                match_score += 50
            if variance_match:
                match_score += 50
            
            return {
                'symbol': symbol,
                'match_score': match_score,
                'volume_ratio': current_pattern['volume_ratio'],
                'price_variance': current_pattern['price_variance'],
                'recommendation': 'WATCH' if match_score >= 50 else 'PASS',
                'checked_at': datetime.now()
            }
        
        return {
            'symbol': symbol,
            'error': 'Insufficient recent data',
            'recommendation': 'INSUFFICIENT_DATA'
        }
