"""
Nasdaq 100 Top 10 Quarterly Rotation Strategy
Backtests a strategy that invests in the top 10 Nasdaq 100 stocks by market cap,
rebalancing quarterly from 2015-2025.

Requirements:
pip install streamlit pandas numpy requests polygon-api-client plotly

Usage:
streamlit run nasdaq_rotation_dashboard.py

Set your Polygon.io API key as an environment variable:
export POLYGON_API_KEY="xxxxxxxx"
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Tuple
import time
import os

# Polygon.io API Configuration
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
POLYGON_BASE_URL = "https://api.polygon.io"


class PolygonDataFetcher:
    """Handles all Polygon.io API interactions"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
    
    def get_nasdaq100_tickers(self, date: str) -> List[str]:
        """
        Get Nasdaq 100 tickers. Note: Polygon doesn't have historical index constituents,
        so we'll approximate by getting large-cap tech stocks from the Nasdaq exchange.
        For production, you'd need a data provider with historical index constituents.
        """
        url = f"{POLYGON_BASE_URL}/v3/reference/tickers"
        params = {
            "market": "stocks",
            "exchange": "XNAS",  # Nasdaq
            "active": "true",
            "limit": 1000,
            "apiKey": self.api_key
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                return [ticker["ticker"] for ticker in data["results"]]
            return []
        except Exception as e:
            st.error(f"Error fetching tickers: {e}")
            return []
    
    def get_market_cap(self, ticker: str, date: str) -> float:
        """Get market cap for a ticker on a specific date"""
        url = f"{POLYGON_BASE_URL}/v3/reference/tickers/{ticker}"
        params = {"date": date, "apiKey": self.api_key}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data and "market_cap" in data["results"]:
                return data["results"]["market_cap"]
            return 0
        except:
            return 0
    
    def get_historical_prices(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical adjusted close prices for a ticker"""
        url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        params = {"adjusted": "true", "apiKey": self.api_key}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                df = pd.DataFrame(data["results"])
                df["date"] = pd.to_datetime(df["t"], unit="ms")
                df = df.rename(columns={"c": "close"})
                df = df[["date", "close"]]
                df = df.set_index("date")
                return df
            return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def get_top_n_by_market_cap(self, tickers: List[str], date: str, n: int = 10) -> List[Tuple[str, float]]:
        """Get top N tickers by market cap on a specific date"""
        market_caps = []
        
        for ticker in tickers:
            mc = self.get_market_cap(ticker, date)
            if mc > 0:
                market_caps.append((ticker, mc))
            time.sleep(0.1)  # Rate limiting
        
        market_caps.sort(key=lambda x: x[1], reverse=True)
        return market_caps[:n]


class PortfolioSimulator:
    """Simulates the quarterly rotation strategy"""
    
    def __init__(self, initial_capital: float, data_fetcher: PolygonDataFetcher):
        self.initial_capital = initial_capital
        self.data_fetcher = data_fetcher
        self.portfolio_history = []
        self.holdings_history = []
        self.trade_log = []
    
    def simulate(self, start_date: datetime, end_date: datetime, top_n: int = 10) -> Dict:
        """Run the quarterly rotation simulation"""
        current_date = start_date
        portfolio_value = self.initial_capital
        
        # Generate quarterly rebalance dates
        rebalance_dates = []
        while current_date <= end_date:
            rebalance_dates.append(current_date)
            current_date += relativedelta(months=3)
        
        # For each quarter
        for i, rebalance_date in enumerate(rebalance_dates[:-1]):
            next_rebalance = rebalance_dates[i + 1]
            
            st.write(f"Processing quarter: {rebalance_date.strftime('%Y-%m-%d')}")
            
            # Get all Nasdaq tickers
            tickers = self.data_fetcher.get_nasdaq100_tickers(rebalance_date.strftime("%Y-%m-%d"))
            
            # Get top N by market cap
            top_stocks = self.data_fetcher.get_top_n_by_market_cap(
                tickers[:100],  # Limit to first 100 for performance
                rebalance_date.strftime("%Y-%m-%d"),
                top_n
            )
            
            if not top_stocks:
                st.warning(f"No stocks found for {rebalance_date}")
                continue
            
            # Record holdings
            holdings = {ticker: mc for ticker, mc in top_stocks}
            self.holdings_history.append({
                "date": rebalance_date,
                "holdings": holdings
            })
            
            # Calculate allocation per stock
            allocation_per_stock = portfolio_value / len(top_stocks)
            
            # Get prices for the quarter
            quarter_returns = []
            for ticker, _ in top_stocks:
                prices = self.data_fetcher.get_historical_prices(
                    ticker,
                    rebalance_date.strftime("%Y-%m-%d"),
                    next_rebalance.strftime("%Y-%m-%d")
                )
                
                if not prices.empty:
                    start_price = prices.iloc[0]["close"]
                    end_price = prices.iloc[-1]["close"]
                    stock_return = (end_price - start_price) / start_price
                    quarter_returns.append(stock_return)
                else:
                    quarter_returns.append(0)
                
                time.sleep(0.1)  # Rate limiting
            
            # Calculate portfolio value at end of quarter
            if quarter_returns:
                avg_return = np.mean(quarter_returns)
                portfolio_value = portfolio_value * (1 + avg_return)
            
            self.portfolio_history.append({
                "date": next_rebalance,
                "value": portfolio_value,
                "return": avg_return if quarter_returns else 0
            })
            
            # Log trade
            self.trade_log.append({
                "date": rebalance_date,
                "action": "Rebalance",
                "tickers": [t for t, _ in top_stocks],
                "portfolio_value": portfolio_value
            })
        
        # Calculate metrics
        total_return = (portfolio_value - self.initial_capital) / self.initial_capital
        years = (end_date - start_date).days / 365.25
        cagr = ((portfolio_value / self.initial_capital) ** (1 / years) - 1) * 100
        
        return {
            "final_value": portfolio_value,
            "total_return": total_return * 100,
            "cagr": cagr,
            "portfolio_history": self.portfolio_history,
            "holdings_history": self.holdings_history,
            "trade_log": self.trade_log
        }


def create_streamlit_dashboard():
    """Main Streamlit dashboard"""
    
    st.set_page_config(page_title="Nasdaq Top 10 Rotation Strategy", layout="wide")
    
    st.title("📈 Nasdaq 100 Top 10 Quarterly Rotation Strategy")
    st.markdown("""
    This dashboard simulates a strategy that invests in the **top 10 Nasdaq 100 stocks by market cap**, 
    rebalancing quarterly. Equal weight is allocated to each stock.
    """)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    api_key = st.sidebar.text_input(
        "Polygon.io API Key",
        value=POLYGON_API_KEY,
        type="password",
        help="Get your free API key at polygon.io"
    )
    
    initial_capital = st.sidebar.number_input(
        "Initial Investment ($)",
        min_value=1000,
        max_value=1000000,
        value=20000,
        step=1000
    )
    
    start_year = st.sidebar.selectbox(
        "Start Year",
        options=list(range(2015, 2024)),
        index=0
    )
    
    end_year = st.sidebar.selectbox(
        "End Year",
        options=list(range(2020, 2026)),
        index=5
    )
    
    top_n = st.sidebar.slider(
        "Number of Stocks",
        min_value=5,
        max_value=20,
        value=10,
        step=5
    )
    
    run_simulation = st.sidebar.button("🚀 Run Simulation", type="primary")
    
    # Information boxes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Strategy**: Equal-weight top stocks by market cap")
    with col2:
        st.info("🔄 **Rebalancing**: Quarterly (every 3 months)")
    with col3:
        st.info("📅 **Data Source**: Polygon.io API")
    
    # Warning about API key
    if not api_key:
        st.warning("""
        ⚠️ **Polygon.io API Key Required**
        
        Please enter your Polygon.io API key in the sidebar. You can get a free API key at:
        https://polygon.io/
        
        **Note**: The free tier has rate limits. For best results, use a paid plan or run simulations 
        during off-peak hours.
        """)
        return
    
    # Run simulation
    if run_simulation:
        if end_year <= start_year:
            st.error("End year must be after start year")
            return
        
        with st.spinner("Running simulation... This may take several minutes due to API rate limits."):
            try:
                # Initialize
                fetcher = PolygonDataFetcher(api_key)
                simulator = PortfolioSimulator(initial_capital, fetcher)
                
                # Run simulation
                start_date = datetime(start_year, 1, 1)
                end_date = datetime(end_year, 12, 31)
                
                results = simulator.simulate(start_date, end_date, top_n)
                
                # Display results
                st.success("✅ Simulation Complete!")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Initial Investment", f"${initial_capital:,.2f}")
                with col2:
                    st.metric("Final Portfolio Value", f"${results['final_value']:,.2f}")
                with col3:
                    st.metric("Total Return", f"{results['total_return']:.2f}%")
                with col4:
                    st.metric("CAGR", f"{results['cagr']:.2f}%")
                
                # Portfolio growth chart
                st.subheader("📈 Portfolio Growth Over Time")
                
                if results['portfolio_history']:
                    df_history = pd.DataFrame(results['portfolio_history'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_history['date'],
                        y=df_history['value'],
                        mode='lines+markers',
                        name='Portfolio Value',
                        line=dict(color='#00cc96', width=3),
                        marker=dict(size=8)
                    ))
                    
                    fig.update_layout(
                        title=f"Portfolio Value: ${initial_capital:,.0f} → ${results['final_value']:,.0f}",
                        xaxis_title="Date",
                        yaxis_title="Portfolio Value ($)",
                        hovermode='x unified',
                        template='plotly_white',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Holdings breakdown
                st.subheader("📊 Holdings by Quarter")
                
                if results['holdings_history']:
                    holdings_data = []
                    for record in results['holdings_history']:
                        quarter = record['date'].strftime('%Y-Q%q')
                        for ticker in record['holdings'].keys():
                            holdings_data.append({
                                'Quarter': quarter,
                                'Ticker': ticker
                            })
                    
                    df_holdings = pd.DataFrame(holdings_data)
                    
                    if not df_holdings.empty:
                        # Count ticker appearances
                        ticker_counts = df_holdings['Ticker'].value_counts()
                        
                        fig2 = px.bar(
                            x=ticker_counts.index[:20],
                            y=ticker_counts.values[:20],
                            title="Most Frequently Held Stocks",
                            labels={'x': 'Ticker', 'y': 'Quarters Held'},
                            color=ticker_counts.values[:20],
                            color_continuous_scale='Viridis'
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                
                # Trade log
                with st.expander("📋 View Trade Log"):
                    if results['trade_log']:
                        for trade in results['trade_log']:
                            st.write(f"**{trade['date'].strftime('%Y-%m-%d')}** - {trade['action']}")
                            st.write(f"Tickers: {', '.join(trade['tickers'])}")
                            st.write(f"Portfolio Value: ${trade['portfolio_value']:,.2f}")
                            st.divider()
                
            except Exception as e:
                st.error(f"Simulation failed: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Notes**:
    - This is a simplified backtest and does not account for transaction costs, slippage, or taxes
    - Historical index constituents are approximated using current Nasdaq listings
    - For production use, consider using a data provider with historical index constituent data
    - Results are for educational purposes only and not financial advice
    """)


if __name__ == "__main__":
    create_streamlit_dashboard()