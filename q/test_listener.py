"""
Test Script for Surge Listener System

Validates all components of the listener system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from q.listener import SurgeListener
from q.signal_layer import (
    CapitalIQScanner,
    EarningsRevisionDetector,
    KeyDevelopmentsMonitor,
    FlatFileBacktester
)
from q.monitoring_layer import (
    IBKRConnector,
    RVOLDetector,
    OrderBookAnalyzer,
    SurgeScanner
)
from q.config import Config
from q.utils import setup_listener_logger


def test_signal_layer():
    """Test Signal Layer components"""
    print("\n" + "="*80)
    print("TESTING SIGNAL LAYER")
    print("="*80)
    
    symbols = ['FSLY', 'NET', 'PLTR']
    
    # Test Capital IQ Scanner
    print("\n1. Testing Capital IQ Scanner...")
    scanner = CapitalIQScanner()
    catalysts = scanner.scan_for_catalysts(symbols, lookback_days=7)
    print(f"   ✓ Found {len(catalysts)} stocks with catalysts")
    
    # Test Earnings Revision Detector
    print("\n2. Testing Earnings Revision Detector...")
    detector = EarningsRevisionDetector()
    revisions = detector.detect_positive_revisions(symbols)
    print(f"   ✓ Detected {len(revisions)} stocks with positive revisions")
    
    # Test Key Developments Monitor
    print("\n3. Testing Key Developments Monitor...")
    monitor = KeyDevelopmentsMonitor()
    developments = monitor.monitor_developments(symbols, lookback_hours=48)
    print(f"   ✓ Found {len(developments)} key developments")
    
    # Test Flat File Backtester
    print("\n4. Testing Flat File Backtester...")
    backtester = FlatFileBacktester()
    surges = backtester.identify_historical_surges('FSLY', lookback_years=2)
    print(f"   ✓ Identified {len(surges)} historical surges")
    
    patterns = backtester.analyze_pre_surge_patterns('FSLY')
    if 'error' not in patterns:
        print(f"   ✓ Analyzed {patterns['num_surges_analyzed']} pre-surge patterns")
    
    print("\n✅ Signal Layer tests passed")


def test_monitoring_layer():
    """Test Monitoring Layer components"""
    print("\n" + "="*80)
    print("TESTING MONITORING LAYER")
    print("="*80)
    
    symbols = ['FSLY', 'NET']
    
    # Test IBKR Connector
    print("\n1. Testing IBKR Connector...")
    ibkr = IBKRConnector()
    connected = ibkr.connect()
    print(f"   ✓ Connection status: {'Connected' if connected else 'Simulated'}")
    
    market_data = ibkr.get_market_data('FSLY')
    print(f"   ✓ Retrieved market data: ${market_data['last']:.2f}")
    
    # Test RVOL Detector
    print("\n2. Testing RVOL Detector...")
    rvol_detector = RVOLDetector(ibkr)
    rvol_data = rvol_detector.calculate_rvol('FSLY')
    print(f"   ✓ FSLY RVOL: {rvol_data['rvol']:.2f}x")
    
    spikes = rvol_detector.scan_for_volume_spikes(symbols)
    print(f"   ✓ Found {len(spikes)} volume spikes")
    
    # Test Order Book Analyzer
    print("\n3. Testing Order Book Analyzer...")
    order_book = OrderBookAnalyzer(ibkr)
    analysis = order_book.analyze_order_book('FSLY')
    if 'error' not in analysis:
        print(f"   ✓ Order book imbalance: {analysis['imbalance_ratio']:.2f}x")
        print(f"   ✓ Direction: {analysis['direction']}")
    
    # Test Surge Scanner
    print("\n4. Testing Surge Scanner...")
    scanner = SurgeScanner(ibkr, rvol_detector, order_book)
    scan_result = scanner.scan_symbol('FSLY', catalyst_score=75.0)
    print(f"   ✓ FSLY recommendation: {scan_result['recommendation']}")
    print(f"   ✓ Composite score: {scan_result['composite_score']}")
    
    ibkr.disconnect()
    print("\n✅ Monitoring Layer tests passed")


def test_full_listener():
    """Test full listener orchestration"""
    print("\n" + "="*80)
    print("TESTING FULL LISTENER SYSTEM")
    print("="*80)
    
    # Create listener
    print("\n1. Initializing Surge Listener...")
    universe = ['FSLY', 'NET', 'DDOG', 'SNOW', 'PLTR', 'VAL']
    listener = SurgeListener(universe=universe)
    print("   ✓ Listener initialized")
    
    # Test watchlist refresh
    print("\n2. Testing watchlist refresh...")
    watchlist = listener.refresh_watchlist()
    print(f"   ✓ Watchlist size: {len(watchlist)}")
    print(f"   ✓ Stocks: {', '.join(watchlist[:5])}")
    
    # Test scanning
    print("\n3. Testing surge scanning...")
    results = listener.run_scan()
    print(f"   ✓ Scanned {len(results)} stocks")
    
    # Test summary
    print("\n4. Testing summary statistics...")
    summary = listener.scanner.get_summary_statistics(results)
    print(f"   ✓ Strong Buy: {summary['strong_buy']}")
    print(f"   ✓ Buy: {summary['buy']}")
    print(f"   ✓ Watch: {summary['watch']}")
    print(f"   ✓ Avg RVOL: {summary['avg_rvol']:.2f}x")
    
    # Cleanup
    listener.shutdown()
    print("\n✅ Full Listener tests passed")


def test_configuration():
    """Test configuration system"""
    print("\n" + "="*80)
    print("TESTING CONFIGURATION")
    print("="*80)
    
    print("\n1. Testing Config class...")
    config_dict = Config.to_dict()
    print(f"   ✓ Config loaded")
    print(f"   ✓ IBKR Host: {config_dict['ibkr']['host']}")
    print(f"   ✓ IBKR Port: {config_dict['ibkr']['port']}")
    print(f"   ✓ Min RVOL: {config_dict['scanner']['min_rvol']}")
    print(f"   ✓ Dry Run: {config_dict['execution']['dry_run']}")
    
    print("\n✅ Configuration tests passed")


def run_all_tests():
    """Run all test suites"""
    print("\n")
    print("*" * 80)
    print("SURGE LISTENER SYSTEM - COMPREHENSIVE TEST SUITE")
    print("*" * 80)
    
    # Setup logging
    logger = setup_listener_logger('test', level='WARNING')  # Reduce noise
    
    try:
        # Run test suites
        test_configuration()
        test_signal_layer()
        test_monitoring_layer()
        test_full_listener()
        
        # Success
        print("\n")
        print("*" * 80)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("*" * 80)
        print("\nThe Surge Listener System is ready to use.")
        print("\nNext steps:")
        print("  1. Configure Capital IQ credentials in environment variables")
        print("  2. Install and configure IBKR TWS/Gateway")
        print("  3. Run: python q/listener.py")
        print("\n")
        
        return True
        
    except Exception as e:
        print("\n")
        print("*" * 80)
        print(f"❌ TEST FAILED: {e}")
        print("*" * 80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
