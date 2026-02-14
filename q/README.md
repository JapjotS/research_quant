# Stock Surge Listener System

A sophisticated listener system that detects stock surges **before they happen** by combining:

1. **Capital IQ Pro** for deep fundamental analysis
2. **Historical flat files** for pattern backtesting  
3. **IBKR Pro API** for real-time execution

## 🎯 Overview

This system identifies stocks poised for major price moves (like FSLY) by detecting the intersection of **catalysts meeting liquidity**. It's not about "price go up" – it's about identifying the conditions that precede surges.

## 🏗️ Architecture

### Two-Layer Design

#### 1. Signal Layer (Capital IQ + Flat Files)
The "kindling" that creates surge potential:

- **Capital IQ Scanner**: Identifies fundamental catalysts
  - Key Developments (Product Launches, Partnerships, Guidance Increases)
  - Analyst Consensus trending upward
  - Sentiment shifts in emerging trends (e.g., Agentic AI infrastructure)

- **Earnings Revision Detector**: Finds stocks where analyst estimates are rising before earnings

- **Key Developments Monitor**: Tracks strategic announcements and partnerships

- **Flat File Backtester**: Analyzes historical surge patterns
  - Volume/Price variance 48 hours before major moves
  - Regression models on the 100 biggest surges
  - Pattern recognition for pre-surge indicators

#### 2. Monitoring Layer (IBKR Pro API)
Real-time market monitoring once Capital IQ narrows the universe from 5,000 stocks to a watchlist of ~50:

- **RVOL Detector**: Identifies volume spikes 3x-5x above 10-day average

- **Order Book Analyzer**: Monitors Level II data for bid/ask imbalances
  - Massive buy interest (bids stacking)
  - Thin ask side
  - Breakout signals

- **Surge Scanner**: Combines all signals with the core logic:
  ```
  IF (CapIQ Sentiment == Positive) 
  AND (Current Volume > 200% of Avg) 
  AND (Price > 20-day EMA) 
  THEN (Execute Buy)
  ```

## 📂 Directory Structure

```
q/
├── signal_layer/                  # Fundamental analysis & pattern recognition
│   ├── capital_iq_scanner.py     # Capital IQ catalyst detection
│   ├── earnings_revision_detector.py  # Earnings estimate momentum
│   ├── key_developments_monitor.py    # Strategic announcements
│   └── flat_file_backtester.py        # Historical pattern analysis
│
├── monitoring_layer/              # Real-time market monitoring
│   ├── ibkr_connector.py         # IBKR TWS API integration
│   ├── rvol_detector.py          # Relative volume spike detection
│   ├── order_book_analyzer.py    # Level II order book analysis
│   └── scanner.py                # Main surge detection logic
│
├── config/                        # Configuration management
│   └── settings.py               # System configuration
│
├── utils/                         # Utility functions
│   ├── logging_utils.py          # Logging setup
│   └── helpers.py                # Helper functions
│
├── listener.py                    # Main orchestrator
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Credentials

Set environment variables:

```bash
# Capital IQ credentials
export CAPITAL_IQ_USERNAME="your_username"
export CAPITAL_IQ_PASSWORD="your_password"
export CAPITAL_IQ_API_KEY="your_api_key"

# IBKR configuration
export IBKR_HOST="127.0.0.1"
export IBKR_PORT="7497"  # 7497 = paper trading, 7496 = live
export IBKR_CLIENT_ID="1"

# Scanner parameters
export MIN_CATALYST_SCORE="60.0"
export MIN_RVOL="2.0"
export MIN_IMBALANCE="1.5"

# Execution settings
export DRY_RUN="true"  # Set to false for live trading
export DEFAULT_POSITION_SIZE="100"
```

Or create a `.env` file in the project root.

### 3. Run the Listener

```bash
cd q
python listener.py
```

## 💡 Usage Examples

### Basic Usage

```python
from q.listener import SurgeListener
from q.utils import setup_listener_logger

# Setup logging
logger = setup_listener_logger('surge_listener', level='INFO')

# Create listener with default universe
listener = SurgeListener()

# Refresh watchlist (run at 8:00 AM daily)
watchlist = listener.refresh_watchlist()

# Run a single scan
results = listener.run_scan()

# Execute opportunities (dry run by default)
listener.execute_opportunities(results)
```

### Custom Universe

```python
# Define your own stock universe
my_universe = ['FSLY', 'NET', 'DDOG', 'SNOW', 'PLTR', 'VAL']

listener = SurgeListener(universe=my_universe)
listener.run_continuous(scan_interval_minutes=5)
```

### Using Individual Components

```python
from q.signal_layer import CapitalIQScanner, FlatFileBacktester
from q.monitoring_layer import IBKRConnector, RVOLDetector

# Capital IQ scanning
scanner = CapitalIQScanner(api_credentials=creds)
catalysts = scanner.scan_for_catalysts(['FSLY', 'NET'])

# Backtest historical patterns
backtester = FlatFileBacktester('./data/historical')
patterns = backtester.analyze_pre_surge_patterns('FSLY', lookback_years=2)

# Monitor real-time volume
ibkr = IBKRConnector()
ibkr.connect()
rvol = RVOLDetector(ibkr)
spikes = rvol.scan_for_volume_spikes(['FSLY', 'NET'])
```

## 🔧 Configuration

Key configuration options in `config/settings.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MIN_CATALYST_SCORE` | 60.0 | Minimum Capital IQ catalyst score |
| `MIN_RVOL` | 2.0 | Minimum relative volume ratio |
| `MIN_IMBALANCE` | 1.5 | Minimum order book imbalance |
| `RVOL_SPIKE_THRESHOLD` | 3.0 | Volume spike threshold (3x-5x) |
| `MAX_WATCHLIST_SIZE` | 50 | Maximum watchlist size |
| `DRY_RUN` | true | Run in simulation mode |

## 📊 Scanner Logic

The core scanner evaluates stocks based on 4 signals:

1. **Catalyst Signal** (30% weight)
   - Capital IQ catalyst score >= threshold
   - Key developments, earnings revisions, partnerships

2. **Volume Signal** (25% weight)
   - RVOL >= 2.0x (current volume vs. 10-day average)
   - Indicates institutional accumulation

3. **Order Book Signal** (25% weight)
   - Bid/Ask imbalance >= 1.5x
   - Heavy buy pressure with thin asks

4. **Price Action Signal** (20% weight)
   - Price > 20-day EMA
   - Confirms uptrend momentum

**Composite Score**: 0-100 based on signal weights

**Recommendations**:
- `STRONG_BUY`: 3+ signals, score >= 75
- `BUY`: 2+ signals, score >= 50  
- `WATCH`: 1+ signals
- `PASS`: No signals

## 📈 Workflow

### Morning Routine (8:00 AM)

1. **Refresh Watchlist**
   - Scan full universe (~5,000 stocks) using Capital IQ
   - Identify top 50 stocks with catalyst potential
   - Detect pre-earnings candidates
   - Monitor key developments

2. **Build Regression Model**
   - Analyze historical surge patterns
   - Calculate typical pre-surge indicators
   - Update thresholds

### Continuous Monitoring (During Market Hours)

1. **Real-Time Scanning** (every 5 minutes)
   - Monitor watchlist for RVOL spikes
   - Analyze order book imbalances
   - Check price vs. 20-day EMA
   
2. **Signal Generation**
   - Combine all signals
   - Calculate composite scores
   - Generate BUY/WATCH recommendations

3. **Execution** (if auto-execute enabled)
   - Place market orders for STRONG_BUY signals
   - Position sizing based on signal strength
   - Risk management

## 🔐 Security & Risk Management

- **Dry Run Mode**: Test strategies without real trades
- **Position Sizing**: Configurable default position size
- **Stop Losses**: Implement your own risk management
- **API Security**: Never commit credentials to version control

## 🛠️ IBKR TWS Setup

1. Download and install [TWS](https://www.interactivebrokers.com/en/index.php?f=16040) or IB Gateway

2. Configure API settings:
   - Enable ActiveX and Socket Clients
   - Set Socket Port: 7497 (paper) or 7496 (live)
   - Trusted IP: 127.0.0.1
   - Allow connections from localhost

3. Start TWS and log in

4. Run the listener - it will connect automatically

## 📚 Data Requirements

### Capital IQ
- Active S&P Capital IQ Pro subscription
- API access enabled
- Historical key developments data
- Consensus estimates data

### Historical Flat Files
Place historical data in `./data/historical/`:
```
data/historical/
├── FSLY.csv
├── VAL.csv
├── AAPL.csv
└── ...
```

Format: CSV with columns `date,open,high,low,close,volume`

### IBKR Market Data
- IBKR Pro subscription
- Real-time market data subscriptions
- Level II (market depth) data for order book analysis

## 🎓 Example: Detecting FSLY-Like Surges

FSLY's surge was driven by:
1. **Catalyst**: Agentic AI infrastructure trend, network traffic growth
2. **Volume**: 5x normal volume 48 hours before breakout
3. **Order Book**: Heavy bid stacking at key levels
4. **Price Action**: Broke above 20-day EMA with momentum

The listener would have detected:
- Trend exposure via keyword matching ("edge computing", "cdn", "ai infrastructure")
- Volume spike 2 days before major move
- Order book imbalance showing institutional buying
- Price > EMA confirming technical setup

→ **STRONG_BUY signal** 24-48 hours before surge

## 📝 Notes

- This is a **professional quant system** - use responsibly
- Always test in paper trading first
- Monitor for false signals and adjust thresholds
- Capital IQ and IBKR subscriptions required for production use
- Simulated data used when APIs not configured

## 🔗 Integration with Main Project

This listener system integrates with the main `research_quant` project:

```python
# Use existing data loader for backtesting
from research_quant.analysis import DataLoader

data_loader = DataLoader(use_spgmiciq=True)
data = data_loader.load_historical_data(['FSLY'], '2022-01-01', '2024-01-01')

# Feed into backtester
from q.signal_layer import FlatFileBacktester
backtester = FlatFileBacktester()
patterns = backtester.analyze_pre_surge_patterns('FSLY')
```

## 🚨 Disclaimer

This software is for educational and research purposes only. Trading stocks involves risk. Past performance does not guarantee future results. Always do your own due diligence and consult with a financial advisor before making investment decisions.

## 📞 Support

For questions or issues:
- Review the main project README
- Check Capital IQ API documentation
- Consult IBKR TWS API documentation
- Review the code comments for implementation details
