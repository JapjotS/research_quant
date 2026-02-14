"""
Volatility Metrics Calculation Module
Implements industry-standard volatility measures for quantitative analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Union
from scipy import stats

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class VolatilityMetrics:
    """
    Calculate various volatility metrics for financial time series data
    Following industry-standard methodologies
    """
    
    def __init__(self, prices: pd.Series, returns: Optional[pd.Series] = None):
        """
        Initialize volatility calculator
        
        Args:
            prices: Price time series (must have datetime index)
            returns: Optional pre-calculated returns series
        """
        self.prices = prices
        self.returns = returns if returns is not None else self._calculate_returns()
        logger.info(f"Initialized VolatilityMetrics with {len(self.prices)} price observations")
    
    def _calculate_returns(self) -> pd.Series:
        """Calculate log returns from prices"""
        return np.log(self.prices / self.prices.shift(1)).dropna()
    
    def realized_volatility(self, window: int = 20, annualization_factor: int = 252) -> pd.Series:
        """
        Calculate realized volatility (rolling standard deviation of returns)
        
        Args:
            window: Rolling window size in trading days
            annualization_factor: Number of trading days per year (default: 252)
            
        Returns:
            Realized volatility series (annualized)
        """
        logger.debug(f"Calculating realized volatility with window={window}")
        vol = self.returns.rolling(window=window).std() * np.sqrt(annualization_factor)
        return vol
    
    def historical_volatility(self, periods: int = 252) -> float:
        """
        Calculate historical volatility over entire sample period
        
        Args:
            periods: Annualization factor (trading days per year)
            
        Returns:
            Annualized historical volatility
        """
        vol = self.returns.std() * np.sqrt(periods)
        logger.info(f"Historical volatility: {vol:.4f} ({vol*100:.2f}%)")
        return vol
    
    def parkinson_volatility(self, high: pd.Series, low: pd.Series, 
                            window: int = 20, annualization_factor: int = 252) -> pd.Series:
        """
        Parkinson's volatility estimator using high-low range
        More efficient than close-to-close volatility
        
        Args:
            high: High prices
            low: Low prices
            window: Rolling window size
            annualization_factor: Trading days per year
            
        Returns:
            Parkinson volatility series
        """
        logger.debug(f"Calculating Parkinson volatility with window={window}")
        hl_ratio = np.log(high / low)
        parkinson = hl_ratio.rolling(window=window).apply(
            lambda x: np.sqrt(np.sum(x**2) / (4 * len(x) * np.log(2))) * np.sqrt(annualization_factor)
        )
        return parkinson
    
    def garman_klass_volatility(self, open_: pd.Series, high: pd.Series, 
                                low: pd.Series, close: pd.Series,
                                window: int = 20, annualization_factor: int = 252) -> pd.Series:
        """
        Garman-Klass volatility estimator
        Uses open, high, low, close prices for more accurate estimation
        
        Args:
            open_: Opening prices
            high: High prices
            low: Low prices
            close: Closing prices
            window: Rolling window size
            annualization_factor: Trading days per year
            
        Returns:
            Garman-Klass volatility series
        """
        logger.debug(f"Calculating Garman-Klass volatility with window={window}")
        
        log_hl = np.log(high / low)
        log_co = np.log(close / open_)
        
        gk = np.sqrt(0.5 * log_hl**2 - (2*np.log(2)-1) * log_co**2)
        gk_vol = gk.rolling(window=window).mean() * np.sqrt(annualization_factor)
        
        return gk_vol
    
    def exponential_weighted_volatility(self, span: int = 20, 
                                       annualization_factor: int = 252) -> pd.Series:
        """
        Exponentially weighted moving average (EWMA) volatility
        More weight on recent observations
        
        Args:
            span: Decay span for EWMA
            annualization_factor: Trading days per year
            
        Returns:
            EWMA volatility series
        """
        logger.debug(f"Calculating EWMA volatility with span={span}")
        ewma_vol = self.returns.ewm(span=span).std() * np.sqrt(annualization_factor)
        return ewma_vol
    
    def get_all_metrics(self, window: int = 20) -> Dict[str, Union[float, pd.Series]]:
        """
        Calculate all available volatility metrics
        
        Args:
            window: Window size for rolling calculations
            
        Returns:
            Dictionary of metric names to values/series
        """
        logger.info("Calculating all volatility metrics")
        
        metrics = {
            'historical_volatility': self.historical_volatility(),
            'realized_volatility': self.realized_volatility(window=window),
            'ewma_volatility': self.exponential_weighted_volatility(span=window),
        }
        
        # Calculate summary statistics
        metrics['volatility_mean'] = metrics['realized_volatility'].mean()
        metrics['volatility_std'] = metrics['realized_volatility'].std()
        metrics['volatility_min'] = metrics['realized_volatility'].min()
        metrics['volatility_max'] = metrics['realized_volatility'].max()
        
        logger.info(f"Calculated {len(metrics)} volatility metrics")
        return metrics
    
    def calculate_var(self, confidence_level: float = 0.95, 
                     holding_period: int = 1) -> float:
        """
        Calculate Value at Risk (VaR) using historical simulation
        
        Args:
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            holding_period: Holding period in days
            
        Returns:
            VaR value
        """
        var = np.percentile(self.returns, (1 - confidence_level) * 100) * np.sqrt(holding_period)
        logger.info(f"VaR ({confidence_level*100}%): {var:.4f} ({var*100:.2f}%)")
        return var
    
    def calculate_cvar(self, confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) / Expected Shortfall
        
        Args:
            confidence_level: Confidence level
            
        Returns:
            CVaR value
        """
        var = self.calculate_var(confidence_level)
        cvar = self.returns[self.returns <= var].mean()
        logger.info(f"CVaR ({confidence_level*100}%): {cvar:.4f} ({cvar*100:.2f}%)")
        return cvar
