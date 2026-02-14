"""
Signal Layer - Fundamental Analysis and Pattern Recognition

This layer identifies stocks with high surge potential using:
- Capital IQ for fundamental triggers (Key Developments, Earnings Revisions)
- Historical flat file analysis for pattern recognition
"""

from .capital_iq_scanner import CapitalIQScanner
from .earnings_revision_detector import EarningsRevisionDetector
from .key_developments_monitor import KeyDevelopmentsMonitor
from .flat_file_backtester import FlatFileBacktester

__all__ = [
    'CapitalIQScanner',
    'EarningsRevisionDetector',
    'KeyDevelopmentsMonitor',
    'FlatFileBacktester'
]
