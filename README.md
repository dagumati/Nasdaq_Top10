# 🚀 Nasdaq 100 Rotation Dashboard & Simulation

**A comprehensive Python application combining a market simulation engine with a dynamic Streamlit dashboard to backtest a quarterly Nasdaq rotation strategy with multiple data provider support.**

-----

## ⚙️ Setup Instructions

Follow these instructions to get the application running on your local machine.

### 1\. Create Virtual Environment

Create and activate a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2\. Install Dependencies

Install all necessary libraries in the virtual environment:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

Or install manually:
```bash
pip install streamlit pandas numpy requests yfinance plotly python-dateutil
```

### 3\. Verify Installation

Check that all packages are installed correctly:

```bash
pip list
```

You should see packages like `streamlit`, `pandas`, `yfinance`, `plotly`, etc.

### 4\. Choose Your Data Provider

The application now supports multiple data providers with different rate limits:

| Provider | Rate Limits | API Key Required | Recommendation |
|----------|-------------|------------------|----------------|
| **Yahoo Finance** | No limits | ❌ No | ⭐ **Recommended** |
| **Financial Modeling Prep** | 250 calls/day (free) | ✅ Yes | 🎯 **Best for historical data** |
| **Finnhub** | 60 calls/min (free) | ✅ Yes | Good alternative |
| **Alpha Vantage** | 5 calls/min (free) | ✅ Yes | Limited free tier |
| **Polygon.io** | 5 calls/min (free) | ✅ Yes | Original provider |

### 5\. Set API Keys (Optional)

Only required if you choose a provider other than Yahoo Finance:

```bash
# For Financial Modeling Prep (recommended for historical data)
export FMP_API_KEY="your_fmp_key_here"

# For Polygon.io
export POLYGON_API_KEY="your_polygon_key_here"

# For Finnhub
export FINNHUB_API_KEY="your_finnhub_key_here"

# For Alpha Vantage
export ALPHA_VANTAGE_API_KEY="your_alpha_vantage_key_here"
```

### 6\. Run the Dashboard

Launch the Streamlit application from your terminal:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the dashboard
streamlit run nasdaq_rotation_dashboard.py
```

**Note:** Always activate the virtual environment before running the application.

-----

## ⚠️ Important Considerations

### Time Period Range (1971-2025)

The simulation supports a wide range of historical periods:

  * **Start Year**: 1971-2023 (default: 2015)
  * **End Year**: 1978-2025 (default: 2020)
  * The backtest relies on actual **historical data** for realistic results.
  * You can adjust the years within the available range using the dashboard sidebar.

**⚠️ Data Availability Note**: 
  * For early years (1970s-1980s), only established companies have historical data
  * Many modern tech companies (Google, Amazon, Tesla, etc.) didn't exist or weren't public yet
  * The system will use fallback lists for periods with limited data availability
  * For best results, consider using start years from 1990 onwards

### Top 10 Stock Selection

The application **directly fetches the top 10 stocks** by market cap for each quarter:

  * **Efficient API Usage**: Only fetches market cap for ~30 major stocks, then selects top 10
  * **Historical Market Cap**: Uses historical market cap data for accurate ranking
  * **Direct Selection**: No need to fetch entire Nasdaq 100 list
  * **Focused Analysis**: Analyzes only the top performers
  * **Fast Performance**: Reduced API calls and processing time

### API Rate Limits & Performance

| Provider | Free Tier Limits | Performance Impact |
|----------|------------------|-------------------|
| **Yahoo Finance** | No limits | ⚡ **Fastest** - No delays |
| **Financial Modeling Prep** | 250 calls/day | 🎯 **Best for historical accuracy** |
| **Finnhub** | 60 calls/min | 🚀 **Fast** - Minimal delays |
| **Alpha Vantage** | 5 calls/min | ⏳ **Slow** - 10-30 min runtime |
| **Polygon.io** | 5 calls/min | ⏳ **Slow** - 10-30 min runtime |

**Recommendation:** 
- Use **Financial Modeling Prep** for the most accurate historical Nasdaq 100 constituents
- Use **Yahoo Finance** for the fastest experience with no rate limits

-----

## 📊 Dashboard Features

### Current Functionality

| Category | Description |
| :--- | :--- |
| **Top 10 Stock Selection** | ✅ Directly fetches top 10 stocks by market cap for each quarter |
| **Multi-API Support** | ✅ Yahoo Finance, Financial Modeling Prep, Finnhub, Alpha Vantage, Polygon.io |
| **Historical Market Cap** | ✅ Uses historical market cap data for accurate ranking |
| **Efficient Processing** | ✅ Only processes ~30 major stocks, selects top 10 |
| **Simulation** | ✅ Quarterly rebalancing simulation |
| **Returns** | ✅ Portfolio growth visualization, CAGR, and total return calculation |
| **Analysis** | ✅ Holdings breakdown by quarter, detailed trade log with timestamps |
| **Configuration** | ✅ Configurable parameters (capital, years, top *N* stocks, API selection) |

### Visual Analytics

  * **Interactive Portfolio Growth Chart**
  * **Most Frequently Held Stocks** bar chart
  * **Detailed Trade Log** with rebalance actions
  * **API Selection Interface** with rate limit information

-----

## 🔧 Suggested Enhancements

These improvements will significantly enhance the accuracy and analytical depth of the simulation.

| Enhancement | Rationale | Code Snippet Idea |
| :--- | :--- | :--- |
| **Transaction Costs** | Essential for modeling real-world brokerage fees and slippage. | `# In PortfolioSimulator.simulate()`<br>`transaction_cost = 0.001`<br>`portfolio_value *= (1 - transaction_cost)` |
| **Dividend Reinvestment** | Incorporate income generated by stocks for a more accurate return. | `url = f"{POLYGON_BASE_URL}/v3/reference/dividends"` |
| **Sector Exposure** | Analyze risk and diversification using Polygon's ticker details endpoint. | `def get_sector(self, ticker: str):` |
| **Benchmark Comparison** | Compare performance against **SPY** or **QQQ** to evaluate alpha. | `# Fetch benchmark data`<br>`Plot side-by-side comparison` |
| **Real Broker Integration** | Enable paper or live trading through a platform like Alpaca. | `from alpaca_trade_api import REST` |

-----

## 🎯 Quick Wins for Better Results

  * **Use Yahoo Finance:** Switch to Yahoo Finance for unlimited API calls and faster performance.
  * **Use Historical Constituent Data:** For optimal accuracy, acquire data from vendors like **Nasdaq Data Link** or **FactSet**.
  * **Optimize API Calls (Caching):** Use libraries like `pickle` to **save market cap and price data locally** and avoid hitting rate limits.
  * **Parallel Processing:** Implement `concurrent.futures` to fetch multiple tickers simultaneously, drastically cutting runtime.
  * **Add Logging:** Implement robust logging for debugging and performance tracking.

-----

## 📈 Expected Performance

Based on historical Nasdaq 100 performance:

  * **CAGR:** 15-20% (varies by period)
  * **Volatility:** Higher than total market due to technology concentration
  * **Max Drawdown:** 30-50% during market corrections

-----

## ➡️ Next Steps

1.  **Create and activate virtual environment** - Follow the setup instructions above.
2.  **Start with Yahoo Finance** - No API key required and no rate limits.
3.  Test with a **small date range first** (e.g., 2020-2022) to verify functionality.
4.  **Monitor API usage** if using other providers to avoid hitting rate limits.
5.  Consider **caching** market cap and price data locally for faster subsequent runs.

## 🔧 Troubleshooting

### Virtual Environment Issues

If you encounter issues with the virtual environment:

```bash
# Remove existing venv and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Package Installation Issues

If packages fail to install:

```bash
# Try installing packages individually
pip install streamlit
pip install pandas
pip install yfinance
pip install plotly
```

### Running the Application

Always ensure the virtual environment is activated:

```bash
# Check if venv is activated (should show venv path)
which python

# If not activated, activate it
source venv/bin/activate
```

## 🆕 What's New

- ✅ **Top 10 Stock Selection**: Directly fetches top 10 stocks by market cap for each quarter
- ✅ **Efficient API Usage**: Only processes ~30 major stocks, selects top 10
- ✅ **Financial Modeling Prep Integration**: Historical market cap data
- ✅ **Historical Market Cap Ranking**: Uses historical market cap for accurate selection
- ✅ **Multi-API Support**: Choose from 5 different data providers
- ✅ **Yahoo Finance Integration**: No rate limits, no API key required
- ✅ **Improved Performance**: Faster simulations with focused stock selection
- ✅ **Better UI**: API selection dropdown with rate limit information
- ✅ **Updated Dependencies**: Added yfinance for Yahoo Finance support
- ✅ **Virtual Environment Setup**: Complete venv setup with all dependencies
- ✅ **Enhanced Documentation**: Step-by-step setup instructions
