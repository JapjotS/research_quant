"""
Visualization Module with Capital IQ Pro Aesthetic
Clean, monochromatic, high-density professional visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
from typing import Optional, Dict, List, Tuple
from tabulate import tabulate

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class CapitalIQVisualizer:
    """
    Professional visualizations following Capital IQ Pro design principles:
    - Monochromatic color scheme (blacks, grays, whites)
    - High information density
    - Clean, minimal design
    - Professional typography
    """
    
    # Capital IQ Pro Color Palette (Monochromatic)
    COLOR_PRIMARY = '#1a1a1a'      # Near black
    COLOR_SECONDARY = '#404040'    # Dark gray
    COLOR_TERTIARY = '#808080'     # Medium gray
    COLOR_ACCENT = '#b3b3b3'       # Light gray
    COLOR_BACKGROUND = '#f5f5f5'   # Off-white
    COLOR_GRID = '#e0e0e0'         # Very light gray
    
    def __init__(self, style: str = 'professional'):
        """
        Initialize visualizer
        
        Args:
            style: Visualization style ('professional', 'minimal')
        """
        self.style = style
        self._configure_matplotlib()
        logger.info("CapitalIQVisualizer initialized")
    
    def _configure_matplotlib(self):
        """Configure matplotlib with Capital IQ Pro aesthetic"""
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Set default parameters
        plt.rcParams.update({
            'figure.facecolor': self.COLOR_BACKGROUND,
            'axes.facecolor': 'white',
            'axes.edgecolor': self.COLOR_SECONDARY,
            'axes.labelcolor': self.COLOR_PRIMARY,
            'axes.grid': True,
            'grid.color': self.COLOR_GRID,
            'grid.linestyle': '-',
            'grid.linewidth': 0.5,
            'grid.alpha': 0.7,
            'text.color': self.COLOR_PRIMARY,
            'xtick.color': self.COLOR_SECONDARY,
            'ytick.color': self.COLOR_SECONDARY,
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
            'font.size': 9,
            'axes.titlesize': 11,
            'axes.labelsize': 9,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'legend.fontsize': 8,
            'figure.titlesize': 12,
            'lines.linewidth': 1.2,
        })
    
    def plot_price_volatility(self, 
                             prices: pd.Series, 
                             volatility: pd.Series,
                             title: str = "Price and Volatility Analysis",
                             figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        Create dual-axis plot of price and volatility
        
        Args:
            prices: Price series
            volatility: Volatility series
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        logger.info("Creating price and volatility plot")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, 
                                       gridspec_kw={'height_ratios': [2, 1]})
        
        # Plot prices
        ax1.plot(prices.index, prices.values, 
                color=self.COLOR_PRIMARY, linewidth=1.5, label='Price')
        ax1.set_ylabel('Price (USD)', fontweight='bold')
        ax1.set_title(title, fontweight='bold', pad=20)
        ax1.legend(loc='upper left', frameon=True, fancybox=False, 
                  edgecolor=self.COLOR_SECONDARY)
        
        # Plot volatility
        ax2.plot(volatility.index, volatility.values * 100, 
                color=self.COLOR_SECONDARY, linewidth=1.5, label='Volatility')
        ax2.fill_between(volatility.index, 0, volatility.values * 100, 
                         alpha=0.2, color=self.COLOR_SECONDARY)
        ax2.set_ylabel('Volatility (%)', fontweight='bold')
        ax2.set_xlabel('Date', fontweight='bold')
        ax2.legend(loc='upper left', frameon=True, fancybox=False,
                  edgecolor=self.COLOR_SECONDARY)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    
    def plot_volatility_distribution(self,
                                    volatility: pd.Series,
                                    title: str = "Volatility Distribution",
                                    figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
        """
        Plot volatility distribution with statistics
        
        Args:
            volatility: Volatility series
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        logger.info("Creating volatility distribution plot")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Clean data
        vol_clean = volatility.dropna() * 100
        
        # Histogram
        n, bins, patches = ax.hist(vol_clean, bins=50, 
                                   color=self.COLOR_TERTIARY, 
                                   alpha=0.7, edgecolor=self.COLOR_PRIMARY)
        
        # Add statistics lines
        mean_vol = vol_clean.mean()
        median_vol = vol_clean.median()
        
        ax.axvline(mean_vol, color=self.COLOR_PRIMARY, 
                  linestyle='--', linewidth=2, label=f'Mean: {mean_vol:.2f}%')
        ax.axvline(median_vol, color=self.COLOR_SECONDARY, 
                  linestyle='-.', linewidth=2, label=f'Median: {median_vol:.2f}%')
        
        ax.set_xlabel('Volatility (%)', fontweight='bold')
        ax.set_ylabel('Frequency', fontweight='bold')
        ax.set_title(title, fontweight='bold', pad=20)
        ax.legend(frameon=True, fancybox=False, edgecolor=self.COLOR_SECONDARY)
        
        plt.tight_layout()
        return fig
    
    def plot_volatility_comparison(self,
                                  volatility_dict: Dict[str, pd.Series],
                                  title: str = "Volatility Metrics Comparison",
                                  figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
        """
        Compare multiple volatility measures
        
        Args:
            volatility_dict: Dictionary of {metric_name: series}
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating comparison plot for {len(volatility_dict)} metrics")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Color palette
        colors = [self.COLOR_PRIMARY, self.COLOR_SECONDARY, 
                 self.COLOR_TERTIARY, self.COLOR_ACCENT]
        linestyles = ['-', '--', '-.', ':']
        
        for i, (name, series) in enumerate(volatility_dict.items()):
            clean_series = series.dropna() * 100
            ax.plot(clean_series.index, clean_series.values,
                   color=colors[i % len(colors)],
                   linestyle=linestyles[i % len(linestyles)],
                   linewidth=1.5,
                   label=name.replace('_', ' ').title())
        
        ax.set_ylabel('Volatility (%)', fontweight='bold')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_title(title, fontweight='bold', pad=20)
        ax.legend(frameon=True, fancybox=False, edgecolor=self.COLOR_SECONDARY)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    
    def create_summary_table(self,
                            metrics: Dict,
                            format_type: str = 'grid') -> str:
        """
        Create professional summary table
        
        Args:
            metrics: Dictionary of metrics
            format_type: Table format ('grid', 'simple', 'fancy_grid')
            
        Returns:
            Formatted table string
        """
        logger.info("Creating summary table")
        
        # Prepare data for table
        table_data = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if abs(value) < 1:
                    formatted_value = f"{value:.4f} ({value*100:.2f}%)"
                else:
                    formatted_value = f"{value:.2f}"
                table_data.append([key.replace('_', ' ').title(), formatted_value])
        
        # Create table
        table = tabulate(table_data, 
                        headers=['Metric', 'Value'],
                        tablefmt=format_type,
                        stralign='left',
                        numalign='right')
        
        return table
    
    def create_correlation_matrix(self,
                                 returns_df: pd.DataFrame,
                                 title: str = "Returns Correlation Matrix",
                                 figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
        """
        Create correlation matrix heatmap
        
        Args:
            returns_df: DataFrame of returns for multiple assets
            title: Plot title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        logger.info("Creating correlation matrix")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Calculate correlation
        corr = returns_df.corr()
        
        # Create heatmap with monochromatic colormap
        sns.heatmap(corr, annot=True, fmt='.2f', 
                   cmap='Greys', center=0,
                   square=True, linewidths=1,
                   cbar_kws={'label': 'Correlation'},
                   ax=ax)
        
        ax.set_title(title, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
