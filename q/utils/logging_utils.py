"""
Logging Utilities for Surge Listener
"""

import logging
import sys
from datetime import datetime
from typing import Optional


def setup_listener_logger(
    name: str = 'surge_listener',
    level: str = 'INFO',
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger for the listener system
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class ListenerLogger:
    """
    Wrapper class for structured logging in the listener system
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def info(self, message: str, **kwargs):
        """Log info message with optional structured data"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional structured data"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.error(message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data"""
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.debug(message)
    
    def scan_event(self, event_type: str, symbol: str, details: dict):
        """Log a scan event"""
        self.info(
            f"SCAN_EVENT: {event_type}",
            symbol=symbol,
            **details
        )
    
    def trade_signal(self, symbol: str, action: str, reason: str):
        """Log a trade signal"""
        self.info(
            f"TRADE_SIGNAL: {action} {symbol}",
            reason=reason,
            timestamp=datetime.now().isoformat()
        )
