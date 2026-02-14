"""
Example: Basic Surge Listener Usage

This example demonstrates how to use the surge listener system
to detect stock surges before they happen.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from q.listener import SurgeListener
from q.utils import setup_listener_logger
from q.config import Config


def example_1_basic_scan():
    """Example 1: Basic watchlist scan"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Watchlist Scan")
    print("=" * 80)
    
    # Setup logger
    logger = setup_listener_logger('example', level='INFO')
    
    # Create listener with a small universe for demonstration
    small_universe = ['FSLY', 'NET', 'DDOG', 'SNOW', 'PLTR', 'VAL', 'NVDA', 'AMD']
    
    listener = SurgeListener(universe=small_universe)
    
    # Refresh watchlist (simulates 8:00 AM routine)
    print("\n1. Refreshing watchlist...")
    watchlist = listener.refresh_watchlist()
    print(f"   Watchlist: {watchlist}")
    
    # Run a scan
    print("\n2. Running surge scan...")
    results = listener.run_scan()
    
    # Display results
    if not results.empty:
        print("\n3. Scan Results:")
        print(results[['symbol', 'recommendation', 'composite_score', 'rvol', 'signal_count']])
        
        # Show opportunities
        opportunities = results[results['recommendation'].isin(['BUY', 'STRONG_BUY'])]
        if not opportunities.empty:
            print(f"\n✓ Found {len(opportunities)} opportunities!")
        else:
            print("\n○ No opportunities at this time")
    
    listener.shutdown()
    print("\n" + "=" * 80 + "\n")


def example_2_individual_components():
    """Example 2: Using individual components"""
    print("=" * 80)
    print("EXAMPLE 2: Using Individual Components")
    print("=" * 80)
    
    from q.signal_layer import CapitalIQScanner, FlatFileBacktester
    from q.monitoring_layer import IBKRConnector, RVOLDetector
    
    # Capital IQ scanning
    print("\n1. Capital IQ Scanner")
    scanner = CapitalIQScanner()
    symbols = ['FSLY', 'NET', 'DDOG']
    catalysts = scanner.scan_for_catalysts(symbols, lookback_days=7)
    print(f"   Found {len(catalysts)} stocks with catalysts")
    if not catalysts.empty:
        print(f"   Top: {catalysts.iloc[0]['symbol']} (score: {catalysts.iloc[0]['catalyst_score']:.1f})")
    
    # Flat file backtesting
    print("\n2. Flat File Backtester")
    backtester = FlatFileBacktester()
    surge_history = backtester.identify_historical_surges('FSLY', lookback_years=2)
    print(f"   Historical surges found: {len(surge_history)}")
    
    # IBKR + RVOL
    print("\n3. RVOL Detector")
    ibkr = IBKRConnector()
    ibkr.connect()
    
    rvol_detector = RVOLDetector(ibkr, spike_threshold=3.0)
    rvol_data = rvol_detector.calculate_rvol('FSLY')
    print(f"   FSLY RVOL: {rvol_data['rvol']:.2f}x")
    
    ibkr.disconnect()
    print("\n" + "=" * 80 + "\n")


def example_3_custom_configuration():
    """Example 3: Custom configuration"""
    print("=" * 80)
    print("EXAMPLE 3: Custom Configuration")
    print("=" * 80)
    
    # Custom configuration
    custom_config = {
        'capital_iq': {'has_credentials': False},
        'ibkr': {
            'host': '127.0.0.1',
            'port': 7497,
            'client_id': 1
        },
        'scanner': {
            'min_catalyst_score': 70.0,  # Higher threshold
            'min_rvol': 2.5,  # Higher threshold
            'min_imbalance': 2.0,  # Higher threshold
            'rvol_spike_threshold': 4.0,  # More aggressive
            'surge_threshold': 0.20  # 20% moves only
        },
        'watchlist': {
            'max_size': 30,  # Smaller, more focused
            'refresh_time': '08:00:00'
        },
        'data': {
            'directory': './data/historical',
            'lookback_years': 2
        },
        'execution': {
            'dry_run': True,
            'default_position_size': 50  # Smaller positions
        },
        'logging': {
            'level': 'INFO'
        }
    }
    
    print("\n1. Creating listener with custom config...")
    print(f"   - Min Catalyst Score: {custom_config['scanner']['min_catalyst_score']}")
    print(f"   - Min RVOL: {custom_config['scanner']['min_rvol']}x")
    print(f"   - Max Watchlist: {custom_config['watchlist']['max_size']}")
    
    listener = SurgeListener(
        config=custom_config,
        universe=['FSLY', 'PLTR', 'SNOW', 'NET']
    )
    
    print("\n2. Running scan with custom thresholds...")
    results = listener.run_scan()
    
    if not results.empty:
        print(f"\n3. Results: {len(results)} stocks scanned")
        high_confidence = results[results['composite_score'] >= 75]
        print(f"   High confidence opportunities: {len(high_confidence)}")
    
    listener.shutdown()
    print("\n" + "=" * 80 + "\n")


def main():
    """Run all examples"""
    print("\n")
    print("*" * 80)
    print("SURGE LISTENER SYSTEM - USAGE EXAMPLES")
    print("*" * 80)
    print("\n")
    
    try:
        # Run examples
        example_1_basic_scan()
        example_2_individual_components()
        example_3_custom_configuration()
        
        print("\n")
        print("*" * 80)
        print("All examples completed successfully!")
        print("*" * 80)
        print("\n")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
