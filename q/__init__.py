"""
Stock Surge Listener System

A comprehensive listener system to detect stock surges before they happen by:
1. Analyzing fundamental catalysts via Capital IQ
2. Backtesting historical patterns from flat files
3. Monitoring real-time market data via IBKR Pro API

Architecture:
- Signal Layer: Capital IQ + Flat Files for fundamental analysis
- Monitoring Layer: IBKR Pro API for real-time monitoring and execution
"""

__version__ = "1.0.0"
