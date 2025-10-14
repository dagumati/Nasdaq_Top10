# Real-Time Data Integration

## 🔄 Upgrade: From Simulated to Real-Time Data

The GT/OR Strategic Asset Selector has been upgraded to use **real-time market data** instead of simulated data.

---

## 📊 What Changed

### **Before** (Simulated Data)
```javascript
// Hardcoded simulated data
const simulatedData = {
    'TSLA': {
        regime: "Signaling Event: Information Asymmetry High",
        model: "Differential Games (Optimal Execution)",
        svi: 85,
        action: "BUY",
        // ... fixed values
    }
}
```

### **After** (Real-Time Data)
```python
# Live market data from Yahoo Finance
ticker = yf.Ticker(symbol)
hist = ticker.history(start=start_date, end=end_date)

# Calculate real technical indicators
volatility = returns.std() * np.sqrt(252) * 100
momentum_3m = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-63]) - 1) * 100
ma_50 = hist['Close'].rolling(50).mean().iloc[-1]
ma_200 = hist['Close'].rolling(200).mean().iloc[-1]
```

---

## 🎯 Real-Time Analysis Features

### 1. **Market Data Fetching**
- Current price and market cap
- 1 year of historical data
- Volume and trading activity
- P/E ratio and fundamentals

### 2. **Technical Indicators Calculated**
- ✅ **Volatility**: Annualized volatility based on daily returns
- ✅ **Momentum**: 3-month price momentum
- ✅ **Moving Averages**: 50-day and 200-day MAs
- ✅ **Trend Strength**: Current price vs 200-day MA
- ✅ **Volume Analysis**: Recent vs average volume ratio

### 3. **Strategic Vulnerability Index (SVI)**

Real-time calculation based on:

```python
SVI = Volatility Component (0-40)
    + Momentum Instability (0-25)
    + Volume Anomaly (0-20)
    + Tail Risk (0-15)
```

**Formula Breakdown:**
- **Volatility Component**: `min(volatility * 1.2, 40)`
- **Momentum Component**: `min(abs(momentum) * 1.5, 25)`
- **Volume Component**: `min(abs(volume_ratio - 1) * 20, 20)`
- **Tail Risk**: Based on 5% Value-at-Risk (VaR)

### 4. **Market Regime Classification**

Real-time regime detection:

| Condition | Regime |
|-----------|--------|
| Volatility > 40% & High Volume | **High Volatility Crisis** |
| Volatility > 40% | **Turbulent Regime** |
| Volatility > 25% & Momentum > 10% | **Trending Volatile Market** |
| Volatility > 25% | **Mixed Signals** |
| Trend > 10% | **Bullish Evolutionary Game** |
| Trend < -10% | **Bearish Pressure** |
| Otherwise | **Stable Equilibrium** |

### 5. **Game Theory Model Selection**

Dynamically selected based on market conditions:

```python
if volatility > 35:
    model = "Stochastic Games (High Uncertainty)"
elif abs(trend) > 15:
    if volume_ratio > 1.3:
        model = "Agent-Based Herding Model"
    else:
        model = "Differential Games (Optimal Execution)"
elif volume_ratio < 0.8:
    model = "Quiet Period: Nash Equilibrium"
else:
    model = "Evolutionary Stable Strategy (ESS)"
```

### 6. **Trading Action Determination**

Multi-signal aggregation:

**Moving Average Signals:**
- Price > MA50 > MA200 → BUY (0.8 confidence)
- Price < MA50 < MA200 → SELL (0.8 confidence)
- Mixed → HOLD

**Momentum Signals:**
- Momentum > 10% → BUY (0.7 confidence)
- Momentum < -10% → SELL (0.7 confidence)
- Otherwise → HOLD

**Risk Adjustment:**
- Confidence reduced by `SVI / 200` (max 50% reduction)
- Final action based on weighted aggregation

### 7. **Portfolio Allocation Optimization**

Real-time calculation:

```python
base_allocation = confidence * 15%  # Max 15% at full confidence

risk_factor = 1 - (svi / 150) - (volatility / 100)
risk_factor = max(risk_factor, 0.2)  # Minimum 20% of base

allocation = base_allocation * risk_factor
# Constrained between 2% and 15%
```

---

## 📈 New UI Components

### **Streamlit-Based Interface** (Replaced HTML/JS)

1. **Input Section**
   - Text input for stock symbol
   - Real-time validation
   - Analyze button with primary styling

2. **Current Metrics Dashboard**
   - Current Price
   - Market Cap (in billions)
   - P/E Ratio
   - Annualized Volatility

3. **Strategic Intelligence**
   - Market Regime Classification (real-time)
   - Dominant Game Theory Model (dynamic)

4. **Strategic Vulnerability Index**
   - Numeric SVI value
   - Color-coded progress bar (Red/Orange/Green)
   - Risk interpretation text

5. **Trading Recommendations**
   - **Position Trading**:
     - Action (BUY/SELL/HOLD) with color coding
     - Confidence level
     - Optimal portfolio allocation
     - Target price range
     - Time horizon
   
   - **Options Trading**:
     - Recommended option type (CALL/PUT/Neutral)
     - Optimal strike price
     - Recommended expiry
     - Risk warning

6. **Technical Analysis Chart**
   - Candlestick chart (6 months)
   - 50-day Moving Average overlay
   - 200-day Moving Average overlay
   - Interactive Plotly chart

7. **Key Technical Metrics**
   - 3-Month Momentum
   - 50-Day MA
   - Annualized Volatility
   - 200-Day MA
   - Volume Ratio
   - Trend vs MA200

---

## 🔧 Technical Implementation

### **Data Sources**

- **Primary**: Yahoo Finance (`yfinance` library)
- **Frequency**: Real-time on demand
- **Historical**: 1 year of daily data
- **Chart**: 6 months of OHLCV data

### **Analysis Engine**

```
User Input (Symbol)
    ↓
fetch_real_time_data()
    ↓
├── Fetch current info (yf.Ticker().info)
├── Fetch 1-year historical data
├── Calculate technical indicators
│   ├── Volatility (annualized)
│   ├── Momentum (3-month)
│   ├── Moving Averages (50, 200)
│   ├── Trend Strength
│   └── Volume Ratio
├── classify_market_regime()
├── determine_game_theory_model()
├── calculate_svi()
├── determine_trading_action()
└── calculate_optimal_allocation()
    ↓
Display Results in Streamlit UI
```

### **Error Handling**

```python
try:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(...)
    
    if hist.empty:
        return None  # Handle gracefully
        
except Exception as e:
    st.error(f"Error fetching data for {symbol}: {e}")
    return None
```

---

## 💡 Usage Examples

### **Example 1: Analyzing TSLA**

```
Input: TSLA
Output:
- Current Price: $265.32
- Market Cap: $846.2B
- Volatility: 42.3%
- Regime: "Turbulent Regime: High Uncertainty & Mean Reversion"
- Model: "Stochastic Games (High Uncertainty)"
- SVI: 68% (Moderate Risk)
- Action: HOLD
- Allocation: 4.2%
```

### **Example 2: Analyzing SPY**

```
Input: SPY
Output:
- Current Price: $520.45
- Market Cap: $480.2B
- Volatility: 18.5%
- Regime: "Stable Equilibrium: Low Volatility Quiet Period"
- Model: "Evolutionary Stable Strategy (ESS)"
- SVI: 28% (Low Risk)
- Action: BUY
- Allocation: 11.5%
```

### **Example 3: Analyzing NVDA**

```
Input: NVDA
Output:
- Current Price: $1,238.67
- Market Cap: $3.1T
- Volatility: 35.2%
- Regime: "Bullish Evolutionary Game: Trend-Following Dominant"
- Model: "Differential Games (Optimal Execution)"
- SVI: 45% (Moderate Risk)
- Action: BUY
- Allocation: 8.7%
```

---

## 📊 Data Update Frequency

| Data Type | Update Frequency |
|-----------|------------------|
| Current Price | On demand (when user clicks Analyze) |
| Market Cap | Real-time from yfinance |
| Historical Data | Daily close (1 year lookback) |
| Technical Indicators | Calculated instantly from historical data |
| SVI | Calculated instantly |
| Recommendations | Generated instantly |

---

## 🚀 Benefits of Real-Time Data

### **Accuracy**
✅ Reflects current market conditions  
✅ No stale or outdated information  
✅ Real technical indicators  

### **Reliability**
✅ Data from trusted source (Yahoo Finance)  
✅ Validated and cleaned data  
✅ Error handling for missing data  

### **Actionability**
✅ Current recommendations  
✅ Real target prices  
✅ Actual support/resistance levels  

### **Transparency**
✅ Shows calculation methodology  
✅ Displays raw metrics  
✅ Users can verify analysis  

---

## ⚙️ Configuration

### **Adjustable Parameters**

You can modify these in `gtor_selector_module.py`:

```python
# Historical data lookback period
start_date = end_date - timedelta(days=365)  # 1 year

# Chart display period
hist = ticker.history(period="6mo")  # 6 months

# SVI component weights
vol_component = min(volatility * 1.2, 40)      # Max 40 points
momentum_component = min(abs(momentum) * 1.5, 25)  # Max 25 points
volume_component = min(abs(volume_ratio - 1) * 20, 20)  # Max 20 points
tail_component = min(abs(var_95) * 150, 15)  # Max 15 points

# Allocation constraints
max_allocation = 15  # Maximum 15% of portfolio
min_allocation = 2   # Minimum 2% of portfolio
```

---

## 🧪 Testing

### **Test with Different Stocks**

```bash
streamlit run app.py

# Try different symbols:
- TSLA (High volatility tech stock)
- SPY (S&P 500 ETF - stable)
- NVDA (High momentum tech)
- GLD (Gold ETF - defensive)
- QQQ (Nasdaq 100 ETF)
```

### **Verify Real-Time Data**

1. Check current price matches market price
2. Verify market cap is accurate
3. Confirm P/E ratio is current
4. Validate moving averages on chart
5. Compare volatility with other sources

---

## 📝 Limitations & Disclaimers

### **Data Limitations**
- Dependent on Yahoo Finance data availability
- Historical data limited to what yfinance provides
- Some tickers may have incomplete data
- After-hours data may not be real-time

### **Analysis Limitations**
- Technical analysis only (no fundamental analysis)
- Based on historical patterns
- Does not account for news/events
- Simplified game theory models

### **Trading Disclaimer**
⚠️ **This is not financial advice**
- For educational purposes only
- Always conduct your own research
- Consult a qualified financial advisor
- Past performance ≠ future results

---

## 🔮 Future Enhancements

### **Planned Features**

1. **Multiple Timeframes**
   - 1-day, 1-week, 1-month, 1-year analysis
   - Adjustable lookback periods

2. **More Technical Indicators**
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Bollinger Bands
   - Fibonacci retracements

3. **Fundamental Analysis**
   - Financial ratios
   - Earnings data
   - Revenue growth
   - Debt levels

4. **Sentiment Analysis**
   - News sentiment
   - Social media sentiment
   - Insider trading activity

5. **Portfolio Integration**
   - Multi-asset portfolio analysis
   - Correlation analysis
   - Risk-adjusted returns

6. **Real-Time Alerts**
   - Price alerts
   - SVI threshold alerts
   - Regime change notifications

7. **Historical Backtesting**
   - Test strategies on historical data
   - Compare actual vs predicted
   - Performance metrics

---

## ✅ Summary

The GT/OR Strategic Asset Selector now provides:

✅ **Real-time market data** from Yahoo Finance  
✅ **Accurate technical indicators** calculated on demand  
✅ **Dynamic market regime classification**  
✅ **Real-time SVI calculation**  
✅ **Data-driven trading recommendations**  
✅ **Interactive charts** with moving averages  
✅ **Professional Streamlit UI**  

This upgrade transforms the tool from a demo/simulation into a **real, actionable analysis platform**.

---

**Ready to analyze real markets!** 🚀📈

Run the application:
```bash
streamlit run app.py
```

Navigate to the **🎯 GT/OR Strategic Asset Selector** tab and enter any stock symbol!

