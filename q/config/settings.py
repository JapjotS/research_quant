"""
Configuration Management for Surge Listener System
"""

import os
from typing import Dict, Optional
import json


class Config:
    """Configuration for the surge listener system"""
    
    # Capital IQ API Configuration
    CAPITAL_IQ_USERNAME = os.getenv('CAPITAL_IQ_USERNAME', '')
    CAPITAL_IQ_PASSWORD = os.getenv('CAPITAL_IQ_PASSWORD', '')
    CAPITAL_IQ_API_KEY = os.getenv('CAPITAL_IQ_API_KEY', '')
    
    # IBKR Configuration
    IBKR_HOST = os.getenv('IBKR_HOST', '127.0.0.1')
    IBKR_PORT = int(os.getenv('IBKR_PORT', '7497'))  # 7497 = paper, 7496 = live
    IBKR_CLIENT_ID = int(os.getenv('IBKR_CLIENT_ID', '1'))
    
    # Scanner Parameters
    MIN_CATALYST_SCORE = float(os.getenv('MIN_CATALYST_SCORE', '60.0'))
    MIN_RVOL = float(os.getenv('MIN_RVOL', '2.0'))
    MIN_IMBALANCE = float(os.getenv('MIN_IMBALANCE', '1.5'))
    RVOL_SPIKE_THRESHOLD = float(os.getenv('RVOL_SPIKE_THRESHOLD', '3.0'))
    SURGE_THRESHOLD = float(os.getenv('SURGE_THRESHOLD', '0.15'))  # 15%
    
    # Watchlist Configuration
    MAX_WATCHLIST_SIZE = int(os.getenv('MAX_WATCHLIST_SIZE', '50'))
    WATCHLIST_REFRESH_TIME = os.getenv('WATCHLIST_REFRESH_TIME', '08:00:00')
    
    # Historical Data Configuration
    DATA_DIRECTORY = os.getenv('DATA_DIRECTORY', './data/historical')
    LOOKBACK_YEARS = int(os.getenv('LOOKBACK_YEARS', '2'))
    
    # Execution Configuration
    DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
    DEFAULT_POSITION_SIZE = int(os.getenv('DEFAULT_POSITION_SIZE', '100'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_capital_iq_credentials(cls) -> Optional[Dict[str, str]]:
        """Get Capital IQ credentials"""
        if cls.CAPITAL_IQ_USERNAME and cls.CAPITAL_IQ_PASSWORD:
            return {
                'username': cls.CAPITAL_IQ_USERNAME,
                'password': cls.CAPITAL_IQ_PASSWORD,
                'api_key': cls.CAPITAL_IQ_API_KEY
            }
        return None
    
    @classmethod
    def get_ibkr_config(cls) -> Dict:
        """Get IBKR connection configuration"""
        return {
            'host': cls.IBKR_HOST,
            'port': cls.IBKR_PORT,
            'client_id': cls.IBKR_CLIENT_ID
        }
    
    @classmethod
    def get_scanner_params(cls) -> Dict:
        """Get scanner parameters"""
        return {
            'min_catalyst_score': cls.MIN_CATALYST_SCORE,
            'min_rvol': cls.MIN_RVOL,
            'min_imbalance': cls.MIN_IMBALANCE,
            'rvol_spike_threshold': cls.RVOL_SPIKE_THRESHOLD,
            'surge_threshold': cls.SURGE_THRESHOLD
        }
    
    @classmethod
    def to_dict(cls) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'capital_iq': {
                'has_credentials': bool(cls.get_capital_iq_credentials())
            },
            'ibkr': cls.get_ibkr_config(),
            'scanner': cls.get_scanner_params(),
            'watchlist': {
                'max_size': cls.MAX_WATCHLIST_SIZE,
                'refresh_time': cls.WATCHLIST_REFRESH_TIME
            },
            'data': {
                'directory': cls.DATA_DIRECTORY,
                'lookback_years': cls.LOOKBACK_YEARS
            },
            'execution': {
                'dry_run': cls.DRY_RUN,
                'default_position_size': cls.DEFAULT_POSITION_SIZE
            },
            'logging': {
                'level': cls.LOG_LEVEL
            }
        }


def load_config_from_file(file_path: str) -> Dict:
    """
    Load configuration from JSON file
    
    Args:
        file_path: Path to JSON configuration file
        
    Returns:
        Configuration dictionary
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def save_config_to_file(config: Dict, file_path: str):
    """
    Save configuration to JSON file
    
    Args:
        config: Configuration dictionary
        file_path: Path to save configuration
    """
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=2)
