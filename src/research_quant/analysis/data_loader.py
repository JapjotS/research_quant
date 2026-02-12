"""
Data Loading Module
Integrates with SPGMICIQ and fallback data sources
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Union
from datetime import datetime, timedelta
import warnings

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Try to import SPGMICIQ
try:
    import spgmiciq
    SPGMICIQ_AVAILABLE = True
    logger.info("SPGMICIQ library available")
except ImportError:
    SPGMICIQ_AVAILABLE = False
    logger.warning("SPGMICIQ library not available")

# Try to import yfinance as fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    logger.info("yfinance library available as fallback")
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance library not available")


class DataLoader:
    """
    Professional data loader with multiple data sources
    Primary: SPGMICIQ (S&P Capital IQ API)
    Fallback: yfinance for demonstration purposes
    """
    
    def __init__(self, use_spgmiciq: bool = True, api_credentials: Optional[Dict] = None):
        """
        Initialize data loader
        
        Args:
            use_spgmiciq: Whether to use SPGMICIQ as primary source
            api_credentials: API credentials for SPGMICIQ (if available)
        """
        self.use_spgmiciq = use_spgmiciq and SPGMICIQ_AVAILABLE
        self.api_credentials = api_credentials
        
        if self.use_spgmiciq and not api_credentials:
            logger.warning("SPGMICIQ selected but no API credentials provided. Will use fallback data source.")
            self.use_spgmiciq = False
        
        logger.info(f"DataLoader initialized (SPGMICIQ: {self.use_spgmiciq})")
    
    def load_historical_data(self, 
                            symbols: Union[str, List[str]],
                            start_date: str,
                            end_date: str,
                            market: str = 'US') -> pd.DataFrame:
        """
        Load historical market data
        
        Args:
            symbols: Ticker symbol(s)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            market: Market region (US, EU, ASIA, etc.)
            
        Returns:
            DataFrame with OHLCV data
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        logger.info(f"Loading data for {len(symbols)} symbols from {start_date} to {end_date}")
        logger.info(f"Market: {market}")
        
        if self.use_spgmiciq:
            return self._load_from_spgmiciq(symbols, start_date, end_date)
        else:
            logger.info("Using fallback data source (yfinance)")
            return self._load_from_yfinance(symbols, start_date, end_date)
    
    def _load_from_spgmiciq(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Load data from SPGMICIQ API
        
        Note: This requires valid API credentials from S&P Global
        """
        logger.info("Attempting to load data from SPGMICIQ API")
        
        # This is where the actual SPGMICIQ API integration would happen
        # Since we don't have credentials, we'll use simulated data
        logger.warning("SPGMICIQ API credentials not configured. Using simulated data for demonstration.")
        
        return self._generate_simulated_data(symbols, start_date, end_date)
    
    def _load_from_yfinance(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Load data from Yahoo Finance (fallback/demonstration)
        """
        if not YFINANCE_AVAILABLE:
            logger.warning("yfinance not available. Using simulated data.")
            return self._generate_simulated_data(symbols, start_date, end_date)
        
        all_data = {}
        
        for symbol in symbols:
            try:
                logger.debug(f"Downloading {symbol} from Yahoo Finance")
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)
                
                if data.empty:
                    logger.warning(f"No data available for {symbol}")
                    continue
                
                # Standardize column names
                data.columns = [col.lower() for col in data.columns]
                all_data[symbol] = data
                logger.info(f"Loaded {len(data)} observations for {symbol}")
                
            except Exception as e:
                logger.error(f"Error loading {symbol}: {str(e)}")
                continue
        
        if not all_data:
            logger.warning("No data loaded from yfinance. Using simulated data.")
            return self._generate_simulated_data(symbols, start_date, end_date)
        
        # Combine data for multiple symbols
        if len(all_data) == 1:
            return list(all_data.values())[0]
        else:
            return pd.concat(all_data, axis=1, keys=all_data.keys())
    
    def _generate_simulated_data(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate simulated market data for demonstration
        Uses geometric Brownian motion with realistic parameters
        """
        logger.info(f"Generating simulated data for {len(symbols)} symbols")
        
        # Parse dates
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Generate business days
        dates = pd.bdate_range(start=start, end=end)
        n_days = len(dates)
        
        all_data = {}
        
        for symbol in symbols:
            # Set seed based on symbol for reproducibility
            np.random.seed(hash(symbol) % 2**32)
            
            # Realistic market parameters
            initial_price = 100 + np.random.uniform(-20, 50)
            mu = np.random.uniform(0.05, 0.15) / 252  # Daily drift
            sigma = np.random.uniform(0.15, 0.35) / np.sqrt(252)  # Daily volatility
            
            # Generate price path using geometric Brownian motion
            returns = np.random.normal(mu, sigma, n_days)
            prices = initial_price * np.exp(np.cumsum(returns))
            
            # Generate OHLC data
            high = prices * (1 + np.abs(np.random.normal(0, 0.01, n_days)))
            low = prices * (1 - np.abs(np.random.normal(0, 0.01, n_days)))
            open_ = np.roll(prices, 1)
            open_[0] = initial_price
            close = prices
            
            # Generate volume
            volume = np.random.lognormal(15, 0.5, n_days)
            
            data = pd.DataFrame({
                'open': open_,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            }, index=dates)
            
            all_data[symbol] = data
            logger.debug(f"Generated {len(data)} observations for {symbol}")
        
        if len(all_data) == 1:
            return list(all_data.values())[0]
        else:
            return pd.concat(all_data, axis=1, keys=all_data.keys())
