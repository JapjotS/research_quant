"""
Main Quantitative Research Portfolio Analysis
Demonstrates professional-grade volatility analysis using SPGMICIQ framework
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from research_quant.analysis import DataLoader, VolatilityMetrics
from research_quant.visualization import CapitalIQVisualizer
from research_quant.utils import setup_logger

# Initialize logger
logger = setup_logger('research_quant.main')


def main():
    """
    Main analysis workflow
    Demonstrates complete quantitative research portfolio capabilities
    """
    logger.info("="*80)
    logger.info("QUANTITATIVE RESEARCH PORTFOLIO - VOLATILITY ANALYSIS")
    logger.info("="*80)
    
    # Configuration
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    logger.info(f"Analysis Period: {start_date} to {end_date}")
    logger.info(f"Symbols: {', '.join(symbols)}")
    
    # Initialize components
    logger.info("\nInitializing components...")
    data_loader = DataLoader(use_spgmiciq=True, api_credentials=None)
    visualizer = CapitalIQVisualizer()
    
    # Load data
    logger.info("\nLoading historical market data...")
    try:
        data = data_loader.load_historical_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            market='US'
        )
        logger.info(f"Data loaded successfully: {data.shape}")
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return
    
    # Analyze each symbol
    results = {}
    
    for symbol in symbols:
        logger.info(f"\n{'='*60}")
        logger.info(f"Analyzing {symbol}")
        logger.info(f"{'='*60}")
        
        try:
            # Extract price data for this symbol
            if len(symbols) > 1:
                symbol_data = data[symbol]
                prices = symbol_data['close']
            else:
                prices = data['close']
            
            # Calculate volatility metrics
            vol_calc = VolatilityMetrics(prices)
            metrics = vol_calc.get_all_metrics(window=20)
            
            # Calculate risk metrics
            var_95 = vol_calc.calculate_var(confidence_level=0.95)
            cvar_95 = vol_calc.calculate_cvar(confidence_level=0.95)
            
            metrics['var_95'] = var_95
            metrics['cvar_95'] = cvar_95
            
            results[symbol] = {
                'prices': prices,
                'metrics': metrics,
                'vol_calc': vol_calc
            }
            
            # Print summary table
            logger.info(f"\nVolatility Metrics for {symbol}:")
            summary_metrics = {
                'Historical Volatility': metrics['historical_volatility'],
                'Mean Realized Vol': metrics['volatility_mean'],
                'Vol Std Dev': metrics['volatility_std'],
                'Min Volatility': metrics['volatility_min'],
                'Max Volatility': metrics['volatility_max'],
                'VaR (95%)': var_95,
                'CVaR (95%)': cvar_95,
            }
            table = visualizer.create_summary_table(summary_metrics)
            print("\n" + table + "\n")
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            continue
    
    # Create visualizations
    logger.info("\n" + "="*80)
    logger.info("CREATING VISUALIZATIONS")
    logger.info("="*80)
    
    # Create output directory
    output_dir = 'examples/output'
    os.makedirs(output_dir, exist_ok=True)
    
    for symbol, result in results.items():
        logger.info(f"\nGenerating plots for {symbol}...")
        
        # Price and volatility plot
        fig1 = visualizer.plot_price_volatility(
            prices=result['prices'],
            volatility=result['metrics']['realized_volatility'],
            title=f"{symbol} - Price and Volatility Analysis"
        )
        fig1.savefig(f"{output_dir}/{symbol}_price_volatility.png", 
                    dpi=300, bbox_inches='tight')
        plt.close(fig1)
        logger.info(f"Saved: {output_dir}/{symbol}_price_volatility.png")
        
        # Volatility distribution
        fig2 = visualizer.plot_volatility_distribution(
            volatility=result['metrics']['realized_volatility'],
            title=f"{symbol} - Volatility Distribution"
        )
        fig2.savefig(f"{output_dir}/{symbol}_volatility_dist.png",
                    dpi=300, bbox_inches='tight')
        plt.close(fig2)
        logger.info(f"Saved: {output_dir}/{symbol}_volatility_dist.png")
        
        # Volatility comparison
        vol_dict = {
            'Realized Vol': result['metrics']['realized_volatility'],
            'EWMA Vol': result['metrics']['ewma_volatility'],
        }
        fig3 = visualizer.plot_volatility_comparison(
            volatility_dict=vol_dict,
            title=f"{symbol} - Volatility Metrics Comparison"
        )
        fig3.savefig(f"{output_dir}/{symbol}_volatility_comparison.png",
                    dpi=300, bbox_inches='tight')
        plt.close(fig3)
        logger.info(f"Saved: {output_dir}/{symbol}_volatility_comparison.png")
    
    # Cross-asset analysis
    if len(results) > 1:
        logger.info("\nCreating cross-asset correlation analysis...")
        
        # Prepare returns data
        returns_dict = {}
        for symbol, result in results.items():
            returns_dict[symbol] = result['vol_calc'].returns
        
        returns_df = pd.DataFrame(returns_dict)
        
        # Correlation matrix
        fig4 = visualizer.create_correlation_matrix(
            returns_df=returns_df,
            title="Returns Correlation Matrix (All Assets)"
        )
        fig4.savefig(f"{output_dir}/correlation_matrix.png",
                    dpi=300, bbox_inches='tight')
        plt.close(fig4)
        logger.info(f"Saved: {output_dir}/correlation_matrix.png")
    
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS COMPLETE")
    logger.info("="*80)
    logger.info(f"\nAll outputs saved to: {output_dir}/")
    
    # Print limitations section
    print_limitations()


def print_limitations():
    """
    Print comprehensive limitations section
    """
    logger.info("\n" + "="*80)
    logger.info("LIMITATIONS AND RISK CONSIDERATIONS")
    logger.info("="*80)
    
    limitations_text = """
    
LIQUIDITY RISK IN NON-US MARKETS

1. Market Depth and Trading Volume
   - Non-US markets, particularly emerging markets, often exhibit significantly
     lower trading volumes compared to US markets
   - Reduced liquidity can lead to wider bid-ask spreads and higher transaction costs
   - Large positions may impact market prices (market impact risk)

2. Market Hours and Fragmentation
   - Different time zones can create gaps in trading continuity
   - Some international markets have shorter trading hours
   - Market fragmentation across multiple exchanges can reduce liquidity pool depth

3. Currency and Settlement Risk
   - Foreign exchange risk compounds liquidity concerns
   - Settlement periods vary by market (T+2, T+3, or longer in some markets)
   - Currency conversion may not always be immediately available at desired rates

4. Regulatory and Market Structure Differences
   - Varying regulatory frameworks can impact market liquidity
   - Different market structures (e.g., auction vs. continuous trading)
   - Capital controls in some jurisdictions may limit liquidity

5. Data Quality and Availability
   - Historical data may be limited or less reliable for some non-US markets
   - Real-time data feeds may have delays or gaps
   - Corporate actions and adjustments may not be uniformly reported

6. Volatility Estimation Challenges
   - Lower trading frequency can bias volatility estimates
   - Irregular trading patterns may violate assumptions of standard volatility models
   - Holiday calendars and market closures differ across regions

7. Crisis and Stress Scenarios
   - Liquidity can evaporate rapidly during market stress
   - Non-US markets may be more susceptible to sudden stops
   - Correlation structures can change dramatically in crisis periods

METHODOLOGICAL LIMITATIONS

1. Model Risk
   - Volatility models assume certain statistical properties that may not hold
   - Historical patterns may not predict future behavior
   - Parameter estimation uncertainty

2. Data Limitations
   - Survivorship bias in historical data
   - Look-ahead bias in backtesting
   - Quality and consistency of data sources

3. Implementation Considerations
   - Theoretical models may not account for real-world frictions
   - Transaction costs, taxes, and regulations impact practical implementation
   - Leverage and margin requirements vary by market

RECOMMENDATIONS

1. Enhanced Due Diligence
   - Conduct thorough liquidity analysis before entering non-US positions
   - Monitor bid-ask spreads and trading volumes continuously
   - Implement appropriate position sizing based on market liquidity

2. Risk Management
   - Use wider risk limits for less liquid markets
   - Implement gradual entry/exit strategies for large positions
   - Maintain adequate capital buffers for liquidity shocks

3. Data Validation
   - Cross-reference multiple data sources when available
   - Implement data quality checks and outlier detection
   - Account for market-specific factors in analysis

4. Continuous Monitoring
   - Track liquidity metrics in real-time
   - Monitor market structure changes and regulatory developments
   - Adjust models and strategies as market conditions evolve

"""
    
    print(limitations_text)
    logger.info("Limitations section complete")


if __name__ == "__main__":
    main()
