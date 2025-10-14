# Application Architecture

## 🏗️ System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         USER                                  │
│                     (Web Browser)                             │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    STREAMLIT SERVER                           │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                     app.py                             │  │
│  │              (Main Entry Point - 47 lines)             │  │
│  │                                                         │  │
│  │  - Page configuration                                  │  │
│  │  - Tab creation                                        │  │
│  │  - Module orchestration                                │  │
│  └──────────────┬───────────────────────┬─────────────────┘  │
│                 │                       │                     │
│                 ▼                       ▼                     │
│  ┌──────────────────────────┐ ┌─────────────────────────┐   │
│  │  nasdaq_rotation_module  │ │  gtor_selector_module   │   │
│  │      (~670 lines)        │ │      (~300 lines)       │   │
│  └──────────────────────────┘ └─────────────────────────┘   │
│                                                               │
└──────────────────┬──────────────────────────────┬────────────┘
                   │                              │
                   ▼                              ▼
         ┌─────────────────┐           ┌──────────────────┐
         │  Yahoo Finance  │           │  Local Storage   │
         │      API        │           │  (HTML/JS/CSS)   │
         └─────────────────┘           └──────────────────┘
```

## 📦 Module Dependency Graph

```
app.py
  │
  ├── imports nasdaq_rotation_module.py
  │       │
  │       ├── OptimizedYahooDataFetcher
  │       │     │
  │       │     └── yfinance API
  │       │
  │       ├── OptimizedPortfolioSimulator
  │       │     │
  │       │     └── OptimizedYahooDataFetcher
  │       │
  │       └── nasdaq_rotation_tab()
  │             │
  │             ├── Streamlit UI components
  │             ├── Plotly charts
  │             └── Pandas DataFrames
  │
  └── imports gtor_selector_module.py
          │
          └── gtor_asset_selector_tab()
                │
                ├── Streamlit components
                └── Embedded HTML/CSS/JS
```

## 🎯 Data Flow Diagram

### Nasdaq Rotation Strategy Flow

```
User Input (Sidebar)
  │
  ├── Initial Capital: $20,000
  ├── Start Year: 2015
  ├── End Year: 2024
  ├── Number of Stocks: 10
  └── Strategy: Full Rebalancing
  │
  ▼
app.py → nasdaq_rotation_tab()
  │
  ▼
OptimizedYahooDataFetcher
  │
  ├── 1. Fetch bulk price data
  │      └── yf.download() → 50 stocks, 2015-2024
  │
  ├── 2. Fetch current info
  │      └── yf.Ticker().info → Market cap, P/E, etc.
  │
  └── 3. Calculate historical market caps
         └── Cache results for reuse
  │
  ▼
OptimizedPortfolioSimulator
  │
  ├── For each quarter:
  │   ├── Get top 10 stocks by market cap
  │   ├── Calculate equal-weight allocation
  │   ├── Simulate trades
  │   └── Track portfolio value
  │
  └── Calculate benchmarks (QQQ, SPY)
  │
  ▼
Results Visualization
  │
  ├── Portfolio value chart
  ├── Holdings breakdown
  ├── Quarterly stock analysis
  └── Trade log
```

### GT/OR Asset Selector Flow

```
User Input
  │
  └── Asset Symbol: TSLA
  │
  ▼
app.py → gtor_asset_selector_tab()
  │
  ▼
Embedded HTML/JavaScript
  │
  ├── 1. Validate input
  │
  ├── 2. Show loading spinner
  │
  ├── 3. Simulate GT/OR analysis
  │      │
  │      ├── Check hardcoded data (TSLA, SPY, GLD)
  │      │
  │      └── OR generate random analysis
  │
  └── 4. Display results
         │
         ├── Market regime classification
         ├── Game theory model
         ├── Strategic Vulnerability Index (SVI)
         ├── Position trading recommendations
         └── Options trading strategy
```

## 🔄 Component Interaction

### Tab Navigation

```
┌─────────────────────────────────────────────────┐
│            Streamlit Tab Bar                    │
├─────────────────────┬───────────────────────────┤
│  📊 Nasdaq Rotation │ 🎯 GT/OR Asset Selector   │
│      (Active)       │                           │
└──────────┬──────────┴───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│    nasdaq_rotation_tab()                 │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │        Sidebar Controls            │ │
│  │  - Initial Capital                 │ │
│  │  - Date Range                      │ │
│  │  - Strategy Selection              │ │
│  │  - [Run Simulation] Button         │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │        Main Content Area           │ │
│  │  - Portfolio Growth Chart          │ │
│  │  - Benchmark Comparison            │ │
│  │  - Holdings Breakdown              │ │
│  │  - Quarterly Analysis              │ │
│  │  - Trade Log                       │ │
│  └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

## 💾 Caching Strategy

```
OptimizedYahooDataFetcher
  │
  ├── _price_cache: Dict[str, pd.DataFrame]
  │     └── Stores: Historical prices for all tickers
  │
  ├── _info_cache: Dict[str, Dict]
  │     └── Stores: Current market cap, P/E, price
  │
  └── _market_cap_cache: Dict[str, float]
        └── Stores: Historical market caps by date
        
Cache Keys:
  - Price cache: ticker (e.g., "AAPL")
  - Market cap cache: "ticker_YYYY-MM-DD" (e.g., "AAPL_2024-01-01")

Cache Benefits:
  ✅ Reduces API calls from 1000+ to ~100
  ✅ 5-10x faster execution
  ✅ Minimizes rate limiting issues
  ✅ Improves user experience
```

## 🎨 UI Component Hierarchy

### Nasdaq Rotation Module UI

```
StreamlitPage
│
├── Header & Description
│
├── Sidebar
│   ├── Configuration Section
│   │   ├── Initial Capital Input
│   │   ├── Start Year Selectbox
│   │   ├── End Year Selectbox
│   │   ├── Number of Stocks Slider
│   │   └── Strategy Selectbox
│   │
│   └── Run Button
│
└── Main Content
    │
    ├── Info Boxes (Optimization Highlights)
    │
    ├── Results Section (Conditional)
    │   │
    │   ├── Metrics Row (3 columns)
    │   │   ├── Final Portfolio Value
    │   │   ├── Total Return
    │   │   └── CAGR
    │   │
    │   ├── Performance Chart (Plotly)
    │   │   ├── Portfolio Value Line
    │   │   ├── QQQ Benchmark Line
    │   │   └── SPY Benchmark Line
    │   │
    │   ├── Holdings Breakdown (Bar Chart)
    │   │
    │   ├── Quarterly Stock Analysis (DataFrame)
    │   │   └── Pagination
    │   │
    │   └── Trade Log (Expandable)
    │
    └── Footer (Optimization Info)
```

### GT/OR Asset Selector UI

```
HTMLDocument (Embedded)
│
├── Header (Gradient Background)
│   ├── Title: "GT/OR Strategic Asset Selector"
│   └── Subtitle
│
├── Input Section
│   ├── Text Input (Asset Symbol)
│   └── Submit Button
│
├── Loading Indicator (Hidden by default)
│   ├── Spinner Animation
│   └── Status Text
│
└── Results Container (Hidden by default)
    │
    ├── Strategic Intelligence Card
    │   ├── Market Regime Classification
    │   └── Dominant Game Theory Model
    │
    └── Prescriptive Policy Card
        │
        ├── Strategic Vulnerability Index
        │   ├── Value Display
        │   ├── Progress Bar (Color-coded)
        │   └── Description Text
        │
        └── Trading Recommendations (2 columns)
            ├── Position Trading Card
            │   ├── Action (BUY/SELL/HOLD)
            │   ├── Optimal Size
            │   ├── Target Price Range
            │   └── Time Horizon
            │
            └── Options Trading Card
                ├── Recommended Option Type
                ├── Optimal Strike Price
                ├── Recommended Expiry
                └── Risk Warning
```

## 🔌 API Integration Points

```
External Dependencies:
│
├── Yahoo Finance (yfinance)
│   │
│   ├── yf.download()
│   │   └── Bulk historical price data
│   │
│   ├── yf.Ticker().info
│   │   └── Current market data
│   │
│   └── yf.Ticker().history()
│       └── Historical OHLCV data
│
├── Plotly
│   └── Interactive charts and graphs
│
├── Pandas
│   └── Data manipulation and analysis
│
├── Streamlit
│   ├── Web framework
│   ├── UI components
│   └── State management
│
└── BeautifulSoup (Future use)
    └── Web scraping for stock screeners
```

## 📊 State Management

```
Streamlit Session State
│
├── Nasdaq Rotation Module State
│   ├── cached_data: Dict
│   │   └── Fetched stock data
│   │
│   ├── simulation_results: Dict
│   │   └── Portfolio simulation output
│   │
│   └── user_inputs: Dict
│       ├── initial_capital
│       ├── start_year
│       ├── end_year
│       ├── top_n
│       └── strategy
│
└── GT/OR Module State
    └── [Managed by JavaScript]
        ├── current_symbol
        ├── analysis_results
        └── ui_state
```

## 🚀 Execution Flow

### Application Startup

```
1. Streamlit loads app.py
   │
   ├── Imports nasdaq_rotation_module
   │   └── Loads classes and functions
   │
   └── Imports gtor_selector_module
       └── Loads UI function
   │
2. main() function executes
   │
   ├── st.set_page_config()
   │   └── Sets page title, icon, layout
   │
   └── Creates tabs
       │
       ├── Tab 1: Calls nasdaq_rotation_tab()
       │
       └── Tab 2: Calls gtor_asset_selector_tab()
   │
3. User interacts with UI
   │
   └── Streamlit reruns on interaction
       │
       └── Preserves session state
```

### Simulation Execution (Nasdaq Rotation)

```
1. User clicks "Run Simulation"
   │
2. Validate inputs
   │
3. Initialize components
   ├── Create OptimizedYahooDataFetcher
   └── Create OptimizedPortfolioSimulator
   │
4. Fetch data (bulk operation)
   ├── Download all price data
   ├── Fetch current info
   └── Calculate market caps
   │
5. Run simulation
   ├── For each quarter:
   │   ├── Select top 10 stocks
   │   ├── Rebalance portfolio
   │   └── Track value
   │
6. Fetch benchmark data
   ├── QQQ prices
   └── SPY prices
   │
7. Calculate metrics
   ├── Final value
   ├── Total return
   └── CAGR
   │
8. Display results
   ├── Render charts
   ├── Show tables
   └── Display trade log
```

## 🎯 Design Patterns Used

### 1. **Module Pattern**
- Separation of concerns
- Each module has a single responsibility

### 2. **Caching Pattern**
- Data is cached to avoid redundant API calls
- Improves performance significantly

### 3. **Factory Pattern**
- Data fetcher classes create data objects
- Portfolio simulator creates simulation results

### 4. **Strategy Pattern**
- Different rebalancing strategies (Full vs Add-Only)
- Selected at runtime

### 5. **Observer Pattern**
- Streamlit watches for UI changes
- Automatically reruns on interaction

## 📈 Performance Optimization

```
Optimization Strategies:
│
├── Bulk Data Fetching
│   └── One API call for all tickers
│       └── 10x faster than individual calls
│
├── Smart Caching
│   ├── Cache prices
│   ├── Cache market caps
│   └── Reuse across quarters
│
├── Early Filtering
│   └── Only fetch data for top candidates
│
└── Lazy Loading
    └── Only fetch when needed
```

## 🔐 Error Handling Strategy

```
Error Handling Layers:
│
├── API Level
│   ├── Try/catch for network errors
│   ├── Fallback to cached data
│   └── User-friendly error messages
│
├── Data Level
│   ├── Validate data integrity
│   ├── Handle missing values
│   └── Filter invalid entries
│
└── UI Level
    ├── Display warnings
    ├── Show progress indicators
    └── Provide feedback
```

## 🎨 Styling and Theming

### Nasdaq Rotation Module
- Uses Streamlit's default theme
- Plotly charts with consistent colors
- Clean, professional layout

### GT/OR Asset Selector
- Custom dark theme
- Tailwind CSS for styling
- Gradient backgrounds
- Smooth animations

---

This architecture document provides a comprehensive overview of the application structure, data flow, and design decisions.

