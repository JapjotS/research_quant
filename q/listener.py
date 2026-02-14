"""
Surge Listener - Main Orchestrator

Coordinates all components to detect stock surges before they happen:
1. Signal Layer: Identifies fundamental catalysts (Capital IQ + Flat Files)
2. Monitoring Layer: Monitors real-time market data (IBKR Pro)
3. Scanner Logic: Combines signals and executes trades

Designed to run continuously with morning watchlist refresh at 8:00 AM
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, time
import pandas as pd

from q.config import Config
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
from q.utils import (
    setup_listener_logger,
    is_market_open,
    format_percentage,
    parse_time_string
)

logger = logging.getLogger(__name__)


class SurgeListener:
    """
    Main orchestrator for the surge detection system.
    
    Coordinates:
    - Capital IQ scanning for fundamental catalysts
    - Flat file backtesting for pattern recognition
    - IBKR real-time monitoring for execution signals
    """
    
    def __init__(
        self,
        config: Optional[Dict] = None,
        universe: Optional[List[str]] = None
    ):
        """
        Initialize the Surge Listener
        
        Args:
            config: Configuration dictionary (uses Config class if None)
            universe: Stock universe to monitor (uses default if None)
        """
        self.config = config or Config.to_dict()
        self.universe = universe or self._get_default_universe()
        
        self.logger = logger
        self.logger.info("="*80)
        self.logger.info("SURGE LISTENER SYSTEM - INITIALIZATION")
        self.logger.info("="*80)
        
        # Initialize components
        self._init_signal_layer()
        self._init_monitoring_layer()
        
        # State
        self.watchlist = []
        self.catalyst_scores = {}
        self.last_watchlist_refresh = None
        
        self.logger.info("Surge Listener initialized successfully")
        self.logger.info(f"Universe size: {len(self.universe)} stocks")
        
    def _get_default_universe(self) -> List[str]:
        """Get default stock universe"""
        # In production, this would load from a file or database
        # For demonstration, use major tech stocks and trending names
        return [
            # FAANG+
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
            # Cloud/Infrastructure (FSLY-like)
            'FSLY', 'NET', 'DDOG', 'SNOW', 'CFLT',
            # AI Infrastructure
            'AMD', 'AVGO', 'QCOM', 'INTC',
            # Growth stocks
            'SHOP', 'SQ', 'ROKU', 'ZM', 'DOCU', 'CRWD',
            # Recent surge candidates
            'VAL', 'PLTR', 'COIN', 'RBLX',
            # Additional tech
            'CRM', 'ORCL', 'ADBE', 'NOW', 'PANW'
        ]
    
    def _init_signal_layer(self):
        """Initialize Signal Layer components"""
        self.logger.info("Initializing Signal Layer...")
        
        # Get Capital IQ credentials
        ciq_creds = Config.get_capital_iq_credentials()
        
        # Initialize scanners
        self.capital_iq_scanner = CapitalIQScanner(api_credentials=ciq_creds)
        self.earnings_detector = EarningsRevisionDetector(api_credentials=ciq_creds)
        self.key_dev_monitor = KeyDevelopmentsMonitor(api_credentials=ciq_creds)
        self.backtester = FlatFileBacktester(
            data_directory=Config.DATA_DIRECTORY
        )
        
        self.logger.info("Signal Layer initialized")
    
    def _init_monitoring_layer(self):
        """Initialize Monitoring Layer components"""
        self.logger.info("Initializing Monitoring Layer...")
        
        # Initialize IBKR connection
        ibkr_config = Config.get_ibkr_config()
        self.ibkr = IBKRConnector(**ibkr_config)
        
        # Connect to IBKR
        connected = self.ibkr.connect()
        if not connected:
            self.logger.warning("Failed to connect to IBKR - using simulated mode")
        
        # Initialize monitoring components
        scanner_params = Config.get_scanner_params()
        
        self.rvol_detector = RVOLDetector(
            self.ibkr,
            spike_threshold=scanner_params['rvol_spike_threshold']
        )
        
        self.order_book_analyzer = OrderBookAnalyzer(
            self.ibkr,
            imbalance_threshold=scanner_params['min_imbalance']
        )
        
        self.scanner = SurgeScanner(
            self.ibkr,
            self.rvol_detector,
            self.order_book_analyzer,
            min_catalyst_score=scanner_params['min_catalyst_score'],
            min_rvol=scanner_params['min_rvol'],
            min_imbalance=scanner_params['min_imbalance']
        )
        
        self.logger.info("Monitoring Layer initialized")
    
    def refresh_watchlist(self) -> List[str]:
        """
        Refresh the watchlist based on Capital IQ signals.
        Designed to run at 8:00 AM daily.
        
        Returns:
            Updated watchlist
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("DAILY WATCHLIST REFRESH - {}".format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        self.logger.info("="*80 + "\n")
        
        # 1. Scan for catalysts using Capital IQ
        self.logger.info("Step 1: Scanning for fundamental catalysts...")
        catalyst_results = self.capital_iq_scanner.scan_for_catalysts(
            self.universe,
            lookback_days=7
        )
        
        # 2. Detect earnings revisions
        self.logger.info("Step 2: Detecting earnings revisions...")
        revision_candidates = self.earnings_detector.get_pre_earnings_candidates(
            self.universe,
            days_ahead=30
        )
        
        # 3. Monitor key developments
        self.logger.info("Step 3: Monitoring key developments...")
        catalyst_stocks = self.key_dev_monitor.get_recent_catalysts(
            self.universe,
            lookback_hours=48
        )
        
        # 4. Combine signals to build watchlist
        self.logger.info("Step 4: Building watchlist...")
        
        # Start with top catalyst scores
        watchlist_set = set()
        
        if not catalyst_results.empty:
            top_catalysts = catalyst_results.head(30)['symbol'].tolist()
            watchlist_set.update(top_catalysts)
            
            # Store catalyst scores
            for _, row in catalyst_results.iterrows():
                self.catalyst_scores[row['symbol']] = row['catalyst_score']
        
        # Add earnings revision candidates
        watchlist_set.update(revision_candidates[:20])
        
        # Add recent catalyst stocks
        watchlist_set.update(catalyst_stocks[:20])
        
        # Convert to list and limit size
        self.watchlist = list(watchlist_set)[:Config.MAX_WATCHLIST_SIZE]
        
        self.last_watchlist_refresh = datetime.now()
        
        self.logger.info(f"\nWatchlist refreshed: {len(self.watchlist)} stocks")
        self.logger.info(f"Top 10: {', '.join(self.watchlist[:10])}")
        
        return self.watchlist
    
    def run_scan(self) -> pd.DataFrame:
        """
        Run a single scan of the watchlist
        
        Returns:
            DataFrame with scan results
        """
        if not self.watchlist:
            self.logger.info("Watchlist empty, refreshing...")
            self.refresh_watchlist()
        
        self.logger.info(f"\nScanning {len(self.watchlist)} stocks...")
        
        # Run the surge scanner
        results = self.scanner.scan_watchlist(
            self.watchlist,
            catalyst_scores=self.catalyst_scores
        )
        
        return results
    
    def execute_opportunities(
        self,
        opportunities: pd.DataFrame,
        dry_run: Optional[bool] = None
    ):
        """
        Execute trades for identified opportunities
        
        Args:
            opportunities: DataFrame with opportunities from scanner
            dry_run: Override config dry_run setting
        """
        if dry_run is None:
            dry_run = Config.DRY_RUN
        
        # Filter to actionable opportunities
        actionable = opportunities[
            opportunities['recommendation'].isin(['BUY', 'STRONG_BUY'])
        ]
        
        if actionable.empty:
            self.logger.info("No actionable opportunities to execute")
            return
        
        self.logger.info(f"\nExecuting {len(actionable)} opportunities...")
        
        for _, opp in actionable.iterrows():
            symbol = opp['symbol']
            
            # Determine position size
            position_size = Config.DEFAULT_POSITION_SIZE
            if opp['recommendation'] == 'STRONG_BUY':
                position_size = int(position_size * 1.5)  # 50% larger for strong signals
            
            # Execute order
            self.scanner.execute_buy_signal(
                symbol=symbol,
                quantity=position_size,
                order_type='MKT',
                dry_run=dry_run
            )
    
    def run_continuous(
        self,
        scan_interval_minutes: int = 5,
        auto_execute: bool = False
    ):
        """
        Run the listener continuously
        
        Args:
            scan_interval_minutes: Minutes between scans
            auto_execute: Automatically execute trades (use with caution!)
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("STARTING CONTINUOUS SURGE LISTENER")
        self.logger.info("="*80)
        self.logger.info(f"Scan interval: {scan_interval_minutes} minutes")
        self.logger.info(f"Auto-execute: {auto_execute}")
        self.logger.info(f"Dry run: {Config.DRY_RUN}")
        
        # Initial watchlist refresh
        self.refresh_watchlist()
        
        # In production, this would run in a loop with proper scheduling
        # For demonstration, we'll run a single cycle
        
        if is_market_open():
            self.logger.info("\nMarket is OPEN - Running scan...")
            
            # Run scan
            results = self.run_scan()
            
            # Show summary
            summary = self.scanner.get_summary_statistics(results)
            self._log_summary(summary)
            
            # Execute if enabled
            if auto_execute and not results.empty:
                self.execute_opportunities(results)
        else:
            self.logger.info("\nMarket is CLOSED - Monitoring mode only")
            self.logger.info("Watchlist prepared for next market open")
    
    def _log_summary(self, summary: Dict):
        """Log scan summary"""
        if 'error' in summary:
            self.logger.warning(f"Summary error: {summary['error']}")
            return
        
        self.logger.info("\n" + "="*80)
        self.logger.info("SCAN SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Total Scanned: {summary['total_scanned']}")
        self.logger.info(f"Strong Buy: {summary['strong_buy']}")
        self.logger.info(f"Buy: {summary['buy']}")
        self.logger.info(f"Watch: {summary['watch']}")
        self.logger.info(f"Pass: {summary['pass']}")
        self.logger.info(f"Avg Composite Score: {summary['avg_composite_score']:.1f}")
        self.logger.info(f"Avg RVOL: {summary['avg_rvol']:.2f}x")
        
        if summary.get('top_opportunities'):
            self.logger.info("\nTop Opportunities:")
            for i, opp in enumerate(summary['top_opportunities'], 1):
                self.logger.info(
                    f"  {i}. {opp['symbol']}: {opp['recommendation']} "
                    f"(Score: {opp['composite_score']:.0f})"
                )
    
    def shutdown(self):
        """Shutdown the listener and cleanup"""
        self.logger.info("\nShutting down Surge Listener...")
        
        # Disconnect from IBKR
        if self.ibkr:
            self.ibkr.disconnect()
        
        self.logger.info("Shutdown complete")


def main():
    """Main entry point"""
    # Setup logging
    logger = setup_listener_logger(
        'surge_listener',
        level=Config.LOG_LEVEL
    )
    
    try:
        # Create and run listener
        listener = SurgeListener()
        
        # Run continuous monitoring
        listener.run_continuous(
            scan_interval_minutes=5,
            auto_execute=False  # Safety: don't auto-execute by default
        )
        
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt signal")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        if 'listener' in locals():
            listener.shutdown()


if __name__ == '__main__':
    main()
