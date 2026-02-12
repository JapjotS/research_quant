"""
Logging configuration for professional-grade logging
Follows Capital IQ Pro aesthetic
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class CapitalIQFormatter(logging.Formatter):
    """Professional formatter with Capital IQ Pro aesthetic"""
    
    # Monochromatic color scheme using ANSI codes
    GREY = "\x1b[38;5;240m"
    WHITE = "\x1b[38;5;255m"
    BOLD = "\x1b[1m"
    RESET = "\x1b[0m"
    
    LEVEL_COLORS = {
        logging.DEBUG: GREY,
        logging.INFO: WHITE,
        logging.WARNING: BOLD + WHITE,
        logging.ERROR: BOLD + WHITE,
        logging.CRITICAL: BOLD + WHITE,
    }
    
    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, self.WHITE)
        
        # Format: [TIMESTAMP] LEVEL | MODULE | MESSAGE
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = f"{record.levelname:8s}"
        module = f"{record.name:30s}"
        
        formatted = f"{self.GREY}[{timestamp}]{self.RESET} {color}{level}{self.RESET} | {self.GREY}{module}{self.RESET} | {color}{record.getMessage()}{self.RESET}"
        
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)
            
        return formatted


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup professional logger with Capital IQ Pro aesthetic
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(CapitalIQFormatter())
    logger.addHandler(console_handler)
    
    return logger
