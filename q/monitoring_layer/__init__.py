"""
Monitoring Layer - Real-time Market Data Analysis via IBKR Pro

This layer monitors real-time market data using IBKR TWS API to detect:
- Relative Volume (RVOL) spikes
- Order Book imbalances
- Price action triggers
"""

from .ibkr_connector import IBKRConnector
from .rvol_detector import RVOLDetector
from .order_book_analyzer import OrderBookAnalyzer
from .scanner import SurgeScanner

__all__ = [
    'IBKRConnector',
    'RVOLDetector',
    'OrderBookAnalyzer',
    'SurgeScanner'
]
