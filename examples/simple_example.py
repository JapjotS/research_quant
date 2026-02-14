"""
Simple example demonstrating the quantitative research portfolio
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime, timedelta
from research_quant.analysis import DataLoader, VolatilityMetrics
from research_quant.visualization import CapitalIQVisualizer

# Initialize components
print("=" * 60)
print("SIMPLE VOLATILITY ANALYSIS EXAMPLE")
print("=" * 60)

# Load data for a single symbol
data_loader = DataLoader(use_spgmiciq=True, api_credentials=None)
symbol = 'AAPL'

# Define date range
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

print(f"\nAnalyzing {symbol} from {start_date} to {end_date}")
print("Loading data...")

# Load historical data
data = data_loader.load_historical_data(
    symbols=symbol,
    start_date=start_date,
    end_date=end_date,
    market='US'
)

# Extract prices
prices = data['close']
print(f"Loaded {len(prices)} price observations")

# Calculate volatility metrics
print("\nCalculating volatility metrics...")
vol_calc = VolatilityMetrics(prices)
metrics = vol_calc.get_all_metrics(window=20)

# Display results
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

print(f"\nHistorical Volatility: {metrics['historical_volatility']:.4f} ({metrics['historical_volatility']*100:.2f}%)")
print(f"Mean Realized Volatility: {metrics['volatility_mean']:.4f} ({metrics['volatility_mean']*100:.2f}%)")
print(f"Volatility Std Dev: {metrics['volatility_std']:.4f} ({metrics['volatility_std']*100:.2f}%)")
print(f"Min Volatility: {metrics['volatility_min']:.4f} ({metrics['volatility_min']*100:.2f}%)")
print(f"Max Volatility: {metrics['volatility_max']:.4f} ({metrics['volatility_max']*100:.2f}%)")

# Calculate risk metrics
var_95 = vol_calc.calculate_var(confidence_level=0.95)
cvar_95 = vol_calc.calculate_cvar(confidence_level=0.95)

print(f"\nValue at Risk (95%): {var_95:.4f} ({var_95*100:.2f}%)")
print(f"Conditional VaR (95%): {cvar_95:.4f} ({cvar_95*100:.2f}%)")

# Create visualization
print("\n" + "=" * 60)
print("Creating visualization...")
visualizer = CapitalIQVisualizer()

fig = visualizer.plot_price_volatility(
    prices=prices,
    volatility=metrics['realized_volatility'],
    title=f"{symbol} - Price and Volatility Analysis"
)

output_path = 'examples/simple_example_output.png'
fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved visualization to: {output_path}")

print("\n" + "=" * 60)
print("EXAMPLE COMPLETE")
print("=" * 60)
