"""
Utility Functions for Surge Listener
"""

from typing import List, Dict
import pandas as pd
from datetime import datetime, time


def parse_time_string(time_str: str) -> time:
    """
    Parse time string to time object
    
    Args:
        time_str: Time string in format 'HH:MM:SS'
        
    Returns:
        time object
    """
    parts = time_str.split(':')
    return time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)


def is_market_open(dt: datetime = None) -> bool:
    """
    Check if US stock market is open
    
    Args:
        dt: Datetime to check (defaults to now)
        
    Returns:
        True if market is open
    """
    if dt is None:
        dt = datetime.now()
    
    # Market hours: 9:30 AM - 4:00 PM ET on weekdays
    if dt.weekday() >= 5:  # Weekend
        return False
    
    market_open = time(9, 30)
    market_close = time(16, 0)
    
    current_time = dt.time()
    
    return market_open <= current_time <= market_close


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format float as percentage string"""
    return f"{value * 100:.{decimals}f}%"


def format_currency(value: float, decimals: int = 2) -> str:
    """Format float as currency string"""
    return f"${value:,.{decimals}f}"


def merge_signals(
    catalyst_data: pd.DataFrame,
    rvol_data: pd.DataFrame,
    order_book_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge signals from different sources
    
    Args:
        catalyst_data: DataFrame with catalyst scores
        rvol_data: DataFrame with RVOL data
        order_book_data: DataFrame with order book data
        
    Returns:
        Merged DataFrame
    """
    # Start with catalyst data
    merged = catalyst_data.copy()
    
    # Merge RVOL data
    if not rvol_data.empty:
        merged = merged.merge(
            rvol_data[['symbol', 'rvol', 'avg_volume']],
            on='symbol',
            how='left'
        )
    
    # Merge order book data
    if not order_book_data.empty:
        merged = merged.merge(
            order_book_data[['symbol', 'imbalance_ratio', 'direction']],
            on='symbol',
            how='left'
        )
    
    return merged


def filter_universe(
    universe: List[str],
    min_price: float = 5.0,
    max_price: float = 1000.0,
    exclude_patterns: List[str] = None
) -> List[str]:
    """
    Filter stock universe based on criteria
    
    Args:
        universe: Full list of symbols
        min_price: Minimum stock price
        max_price: Maximum stock price
        exclude_patterns: List of patterns to exclude (e.g., ['SPAC', 'ETF'])
        
    Returns:
        Filtered list of symbols
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    filtered = []
    for symbol in universe:
        # Check exclusion patterns
        should_exclude = any(pattern.lower() in symbol.lower() for pattern in exclude_patterns)
        
        if not should_exclude:
            filtered.append(symbol)
    
    return filtered


def rank_opportunities(
    opportunities: pd.DataFrame,
    weights: Dict[str, float] = None
) -> pd.DataFrame:
    """
    Rank opportunities based on weighted scoring
    
    Args:
        opportunities: DataFrame with opportunities
        weights: Dictionary with weights for different factors
        
    Returns:
        DataFrame with ranked opportunities
    """
    if weights is None:
        weights = {
            'catalyst_score': 0.30,
            'rvol': 0.25,
            'imbalance_ratio': 0.25,
            'composite_score': 0.20
        }
    
    # Normalize scores to 0-100 scale
    df = opportunities.copy()
    
    for col in weights.keys():
        if col in df.columns:
            max_val = df[col].max()
            if max_val > 0:
                df[f'{col}_norm'] = (df[col] / max_val) * 100
            else:
                df[f'{col}_norm'] = 0
    
    # Calculate weighted rank score
    df['rank_score'] = 0
    for col, weight in weights.items():
        norm_col = f'{col}_norm'
        if norm_col in df.columns:
            df['rank_score'] += df[norm_col] * weight
    
    # Sort by rank score
    df = df.sort_values('rank_score', ascending=False)
    
    return df
