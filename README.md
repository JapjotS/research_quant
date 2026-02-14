# Quantitative Research Portfolio

**Professional-Grade Volatility Analysis & Stock Surge Detection Using SPGMICIQ**

A comprehensive quantitative research platform designed with Capital IQ Pro aesthetic principles, featuring advanced volatility metrics, high-density data visualizations, institutional-grade analytics, and a sophisticated **stock surge detection system**.

---

## 🎯 Overview

This project implements a professional quantitative research portfolio that:

- **Leverages SPGMICIQ**: Integrates with S&P Capital IQ API for institutional-quality market data
- **Calculates Advanced Volatility Metrics**: Implements multiple industry-standard volatility measures
- **Capital IQ Pro Aesthetic**: Clean, monochromatic visualizations with high information density
- **Professional Logging**: Comprehensive logging system for production-grade applications
- **Risk Analysis**: VaR, CVaR, and cross-asset correlation analysis
- **🆕 Stock Surge Listener**: Real-time system to detect surges before they happen (see [`q/`](q/) directory)
- **Comprehensive Documentation**: Including limitations discussion for non-US markets

---

## 🚀 NEW: Stock Surge Listener System

The **`q/` directory** contains a powerhouse listener system that detects stock surges **before they happen** by combining:

- **Capital IQ Pro** for deep fundamental analysis (catalysts, earnings revisions, key developments)
- **Historical flat files** for pattern backtesting and regression models
- **IBKR Pro TWS API** for real-time monitoring and execution

### Key Features

✅ **Signal Layer**: Identifies fundamental catalysts that create surge potential  
✅ **Monitoring Layer**: Real-time RVOL spikes, order book imbalances, price action  
✅ **Scanner Logic**: Combines all signals → `IF (Catalyst + Volume + OrderBook + Price) THEN BUY`  
✅ **Daily Watchlist Refresh**: Automatically narrows 5,000 stocks to top 50 candidates  
✅ **Production-Ready**: Dry-run mode, position sizing, comprehensive logging  

**See [`q/README.md`](q/README.md) for complete documentation and usage examples.**

### Quick Start (Listener System)

```bash
# Install dependencies (includes ib_insync for IBKR)
pip install -r requirements.txt

# Configure credentials (optional for demo)
export CAPITAL_IQ_USERNAME="your_username"
export CAPITAL_IQ_PASSWORD="your_password"
export IBKR_PORT="7497"  # Paper trading

# Run the listener
cd q
python listener.py

# Or run examples
python examples.py
```

---

## 📋 Features

### Data Integration
- **Primary**: SPGMICIQ (S&P Capital IQ API) integration
- **Fallback**: Yahoo Finance for demonstration purposes
- **Simulated Data**: Realistic market data generation for testing

### Volatility Metrics
- **Realized Volatility**: Rolling standard deviation of returns
- **Historical Volatility**: Full-sample volatility estimation
- **Parkinson Volatility**: High-low range estimator
- **Garman-Klass Volatility**: OHLC-based estimator
- **EWMA Volatility**: Exponentially weighted moving average
- **VaR & CVaR**: Value at Risk and Conditional Value at Risk

### Professional Visualizations
- Price and volatility dual-axis plots
- Volatility distribution histograms with statistics
- Multi-metric comparison charts
- Correlation matrices
- Capital IQ Pro monochromatic aesthetic
- High-density, clean design

### Logging & Monitoring
- Professional-grade logging with timestamps
- Color-coded severity levels
- Module-level tracking
- Production-ready format

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/JapjotS/research_quant.git
cd research_quant

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run the main analysis
python main.py
```

This will:
1. Load historical data for major tech stocks (AAPL, MSFT, GOOGL, AMZN)
2. Calculate comprehensive volatility metrics
3. Generate professional visualizations
4. Output analysis to `examples/output/`
5. Display limitations and risk considerations

### Output

The analysis generates:
- **Summary Tables**: Clean, formatted metric tables
- **Visualizations**: High-quality PNG charts (300 DPI)
- **Logs**: Detailed execution logs
- **Limitations Report**: Comprehensive risk analysis

---

## 📊 Example Output

### Volatility Metrics Summary

```
Metric                          Value
----------------------------  -------
Historical Volatility          0.2847 (28.47%)
Mean Realized Vol              0.2756 (27.56%)
Vol Std Dev                    0.0423 (4.23%)
Min Volatility                 0.1234 (12.34%)
Max Volatility                 0.4521 (45.21%)
VaR (95%)                     -0.0234 (-2.34%)
CVaR (95%)                    -0.0312 (-3.12%)
```

### Visualizations
- Price and volatility time series
- Volatility distribution with statistics
- Multi-metric volatility comparison
- Cross-asset correlation heatmap

*All visualizations follow Capital IQ Pro aesthetic: monochromatic, high-density, professional*

---

## 🏗️ Project Structure

```
research_quant/
├── src/
│   └── research_quant/
│       ├── __init__.py
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── data_loader.py      # Data integration (SPGMICIQ, yfinance)
│       │   └── volatility.py       # Volatility calculations
│       ├── visualization/
│       │   ├── __init__.py
│       │   └── visualizer.py       # Capital IQ Pro visualizations
│       └── utils/
│           ├── __init__.py
│           └── logger.py           # Professional logging
├── q/                              # 🆕 Stock Surge Listener System
│   ├── signal_layer/              # Capital IQ + Flat File analysis
│   │   ├── capital_iq_scanner.py
│   │   ├── earnings_revision_detector.py
│   │   ├── key_developments_monitor.py
│   │   └── flat_file_backtester.py
│   ├── monitoring_layer/          # IBKR real-time monitoring
│   │   ├── ibkr_connector.py
│   │   ├── rvol_detector.py
│   │   ├── order_book_analyzer.py
│   │   └── scanner.py
│   ├── config/                    # Configuration management
│   ├── utils/                     # Utilities for listener
│   ├── listener.py                # Main orchestrator
│   ├── examples.py                # Usage examples
│   ├── test_listener.py           # Comprehensive tests
│   └── README.md                  # Listener documentation
├── examples/
│   └── output/                     # Generated charts and reports
├── tests/                          # Unit tests
├── main.py                         # Main volatility analysis script
├── requirements.txt                # Dependencies (includes ib_insync)
└── README.md                       # This file
```

---

## 🔧 API Integration

### Using SPGMICIQ with Real Credentials

```python
from research_quant.analysis import DataLoader

# Initialize with S&P Capital IQ credentials
data_loader = DataLoader(
    use_spgmiciq=True,
    api_credentials={
        'username': 'your_username',
        'password': 'your_password',
        # Add other required credentials
    }
)

# Load data
data = data_loader.load_historical_data(
    symbols=['AAPL', 'MSFT'],
    start_date='2022-01-01',
    end_date='2024-01-01',
    market='US'
)
```

### Custom Analysis

```python
from research_quant.analysis import VolatilityMetrics
from research_quant.visualization import CapitalIQVisualizer

# Calculate volatility
vol_metrics = VolatilityMetrics(prices)
metrics = vol_metrics.get_all_metrics(window=20)

# Visualize
viz = CapitalIQVisualizer()
fig = viz.plot_price_volatility(
    prices=prices,
    volatility=metrics['realized_volatility'],
    title="Custom Analysis"
)
fig.savefig('output.png', dpi=300, bbox_inches='tight')
```

---

## ⚠️ Limitations

### Liquidity Risk in Non-US Markets

This portfolio includes a comprehensive limitations section addressing:

1. **Market Depth and Trading Volume**
   - Lower liquidity in emerging markets
   - Wider bid-ask spreads
   - Market impact risk for large positions

2. **Market Hours and Fragmentation**
   - Time zone considerations
   - Varying trading hours
   - Exchange fragmentation

3. **Currency and Settlement Risk**
   - FX risk in international markets
   - Variable settlement periods
   - Currency conversion constraints

4. **Regulatory Differences**
   - Varying regulatory frameworks
   - Different market structures
   - Capital controls

5. **Data Quality Challenges**
   - Limited historical data availability
   - Real-time data delays
   - Inconsistent corporate action reporting

6. **Volatility Estimation Issues**
   - Low trading frequency bias
   - Assumption violations
   - Calendar differences

7. **Crisis Scenarios**
   - Liquidity evaporation
   - Sudden stops risk
   - Correlation breakdown

### Methodological Limitations

- Model risk and parameter uncertainty
- Data quality and availability constraints
- Implementation frictions (costs, taxes, regulations)

For complete details, see the Limitations section in the analysis output.

---

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest tests/

# Run with coverage
pytest --cov=src/research_quant tests/
```

---

## 📈 Advanced Usage

### Analyzing Non-US Markets

```python
# Example: European market analysis
data_loader = DataLoader(use_spgmiciq=True, api_credentials=credentials)
data = data_loader.load_historical_data(
    symbols=['BMW.DE', 'SAP.DE', 'SIE.DE'],
    start_date='2023-01-01',
    end_date='2024-01-01',
    market='EU'
)
```

### Custom Volatility Windows

```python
# Short-term volatility (5-day window)
short_vol = vol_metrics.realized_volatility(window=5)

# Medium-term volatility (20-day window)
medium_vol = vol_metrics.realized_volatility(window=20)

# Long-term volatility (60-day window)
long_vol = vol_metrics.realized_volatility(window=60)
```

### Multi-Asset Portfolio Analysis

```python
# Analyze correlations across assets
returns_df = pd.DataFrame({
    'AAPL': aapl_returns,
    'MSFT': msft_returns,
    'GOOGL': googl_returns
})

viz = CapitalIQVisualizer()
fig = viz.create_correlation_matrix(returns_df)
```

---

## 🔗 Integrating Volatility Analysis with Surge Detection

The volatility analysis tools and surge listener work together seamlessly:

```python
from research_quant.analysis import DataLoader, VolatilityMetrics
from q.signal_layer import FlatFileBacktester
from q.listener import SurgeListener

# 1. Use volatility analysis to identify high-volatility candidates
data_loader = DataLoader(use_spgmiciq=True)
data = data_loader.load_historical_data(['FSLY', 'NET'], '2023-01-01', '2024-01-01')

vol_metrics = VolatilityMetrics(data['close'])
high_vol_stocks = vol_metrics.get_all_metrics(window=20)

# 2. Backtest these stocks for surge patterns
backtester = FlatFileBacktester()
patterns = backtester.analyze_pre_surge_patterns('FSLY', lookback_years=2)

# 3. Monitor in real-time with the listener
listener = SurgeListener(universe=['FSLY', 'NET'])
listener.run_continuous(scan_interval_minutes=5)
```

**Use Case**: First identify high-volatility stocks, then use the backtester to find pre-surge patterns, and finally monitor them in real-time for actual surge signals.

---

## 📚 Dependencies

### Core Libraries
- **spgmiciq** (>=3.0.0): S&P Capital IQ API Client
- **pandas** (>=1.5.0): Data manipulation
- **numpy** (>=1.23.0): Numerical computing
- **matplotlib** (>=3.5.0): Visualization
- **seaborn** (>=0.12.0): Statistical visualization
- **scipy** (>=1.9.0): Scientific computing
- **yfinance** (>=0.2.0): Fallback data source
- **tabulate** (>=0.9.0): Table formatting
- **colorama** (>=0.4.6): Colored terminal output

### Surge Listener (q/ directory)
- **ib_insync** (>=0.9.86): Interactive Brokers TWS API integration

See `requirements.txt` for complete list.

---

## 🎨 Design Principles

### Capital IQ Pro Aesthetic

1. **Monochromatic Color Scheme**
   - Primary: #1a1a1a (Near black)
   - Secondary: #404040 (Dark gray)
   - Tertiary: #808080 (Medium gray)
   - Accent: #b3b3b3 (Light gray)
   - Background: #f5f5f5 (Off-white)

2. **High Information Density**
   - Maximize data-to-ink ratio
   - Minimal decorative elements
   - Clear hierarchies

3. **Professional Typography**
   - Sans-serif fonts (Arial, DejaVu Sans)
   - Consistent sizing
   - Clear labels and legends

4. **Clean Layout**
   - Grid-aligned elements
   - Adequate white space
   - Logical flow

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

This project is provided as-is for educational and research purposes.

---

## 👥 Author

Quantitative Research Team

---

## 🙏 Acknowledgments

- **S&P Global**: For the SPGMICIQ API platform
- **Capital IQ Pro**: For design inspiration
- **Quantitative Finance Community**: For methodological standards

---

## 📞 Support

For questions or issues:
- **Volatility Analysis**: Review this README and main.py documentation
- **Surge Listener**: See [q/README.md](q/README.md) for detailed documentation
- Open an issue on GitHub
- Check the limitations section
- Review Capital IQ API and IBKR TWS API documentation

---

## 🌟 Highlights

### Two Powerful Systems in One Repository

1. **Volatility Analysis** (`src/research_quant/`)
   - Professional-grade volatility metrics
   - Capital IQ Pro aesthetic visualizations
   - Institutional-quality risk analysis
   - Perfect for research and reporting

2. **Surge Detection** (`q/`)
   - Real-time stock surge prediction
   - Combines fundamentals + technicals + order flow
   - Automated watchlist management
   - Production-ready execution framework

**Together**: Create a complete quantitative research and trading platform.

---

**Built with professional standards. Designed for institutional use.**