# Architecture — Global Investment Research Platform v2.0

[![GitHub](https://img.shields.io/badge/GitHub-dagumati%2FNasdaq__Top10-181717?logo=github)](https://github.com/dagumati/Nasdaq_Top10)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│                                                                     │
│  React 18 SPA (Vite)       Streamlit Dashboard (legacy)             │
│  ├── React Router v6        ├── Global Research Tab                 │
│  ├── Recharts               ├── Weekly DCA Tab                      │
│  ├── Axios + interceptors   └── Nasdaq Rotation Tab                 │
│  └── Dark / Light Theme                                             │
└────────────────────┬────────────────────────────┬───────────────────┘
                     │ HTTP /api/*                 │ Direct Python import
┌────────────────────▼───────────────┐     ┌──────▼──────────────────┐
│      FastAPI Backend (v2.0)        │     │  Streamlit App (app.py) │
│                                    │     └─────────────────────────┘
│  /api/screener/*                   │
│  /api/recommendations/*            │
│  /api/portfolio/*                  │
│  /api/dca/*                        │
│  /api/nasdaq/*                     │
│  /api/health                       │
└────────────────────┬───────────────┘
                     │ Python imports
┌────────────────────▼───────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                              │
│                                                                     │
│  global_research_module.py    weekly_dca_module.py                  │
│  ├── GlobalResearchEngine     ├── DCASimulator                      │
│  │   ├── fetch_asset_data()   │   ├── simulate_dca()               │
│  │   ├── calculate_scores()   │   └── _data_cache                  │
│  │   ├── screen_universe()    └── GrowthProjector                  │
│  │   └── _score_cache             └── project_growth()             │
│  └── ModelPortfolioBuilder    nasdaq_rotation_module.py            │
│      └── 4 portfolios         ├── OptimizedYahooDataFetcher        │
│                               └── OptimizedPortfolioSimulator      │
└────────────────────┬───────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────────┐
│                   DATA LAYER                                        │
│                                                                     │
│  yfinance (primary)    FMP API (optional)   Finnhub (optional)     │
│  ├── Price history     Financial data       Real-time quotes       │
│  ├── Current prices    Fundamentals         Earnings               │
│  └── Market metadata   Dividends            Analyst ratings        │
└────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
Nasdaq_Top10/
│
├── app.py                          # Streamlit entry point (5 tabs)
├── requirements.txt                # Python dependencies (root)
│
├── backend/                        # FastAPI REST backend (NEW v2.0)
│   ├── main.py                     # App factory, CORS, router registration
│   ├── requirements.txt            # Backend-specific deps (fastapi, uvicorn)
│   ├── models/
│   │   └── schemas.py              # Pydantic request/response models
│   ├── routers/
│   │   ├── screener.py             # GET /api/screener/*
│   │   ├── recommendations.py      # GET /api/recommendations/*
│   │   ├── portfolio.py            # GET /api/portfolio/*
│   │   ├── dca.py                  # GET /api/dca/*
│   │   └── nasdaq.py               # GET /api/nasdaq/*
│   └── tests/
│       └── test_api.py             # pytest test suite
│
├── frontend/                       # React 18 frontend (NEW v2.0)
│   ├── package.json
│   ├── vite.config.js              # Vite + /api proxy to :8000
│   ├── index.html
│   ├── .babelrc
│   ├── jest.config.cjs
│   └── src/
│       ├── main.jsx                # ReactDOM.createRoot
│       ├── App.jsx                 # Routes
│       ├── styles/global.css       # CSS design system (dark + light)
│       ├── context/
│       │   └── ThemeContext.jsx    # Dark/light theme provider
│       ├── services/
│       │   └── api.js              # Axios API service layer
│       ├── hooks/
│       │   └── useApi.js           # Generic async API hook
│       ├── components/
│       │   ├── Layout/
│       │   │   ├── Layout.jsx      # Shell + health check
│       │   │   ├── Sidebar.jsx     # Fixed nav with active indicators
│       │   │   └── Navbar.jsx      # Title + theme toggle + API status
│       │   ├── Cards/
│       │   │   ├── MetricCard.jsx  # KPI metric display
│       │   │   └── SharedUI.jsx    # RatingBadge, ScoreBar, formatters
│       │   └── Tables/
│       │       └── ScreenerTable.jsx  # Sortable results table
│       └── pages/
│           ├── Dashboard.jsx          # Home — feature cards + metrics
│           ├── GlobalScreener.jsx     # Screener + radar + scatter chart
│           ├── WeeklyRecommendations.jsx  # Picks + pie chart
│           ├── ModelPortfolios.jsx    # 4 portfolios + holdings + pie
│           ├── DCASimulator.jsx       # Growth projection + backtest
│           └── NasdaqRotation.jsx     # Rotation simulation + charts
│
├── global_research_module.py       # Core research engine
├── weekly_dca_module.py            # DCA simulator & growth projector
├── global_research_dashboard.py    # Streamlit dashboard (3 tabs)
├── nasdaq_rotation_module.py       # Nasdaq rotation logic
├── nasdaq_rotation_dashboard.py    # Streamlit Nasdaq tab
├── gtor_selector_module.py         # GT/OR asset selector
│
├── README.md
├── ARCHITECTURE.md                 # This file
├── QUICKSTART.md
├── MODULE_STRUCTURE.md
├── HOSTING_GUIDE.md                # NEW — deployment guide
└── venv/                           # Python virtual environment
```

---

## Data Flow

### Screener Request (React → API → yfinance)

```
User clicks "Run Screener"
    │
    ▼
GlobalScreener.jsx
    │  GET /api/screener/run?universe=thematic&top_n=15
    ╠══════════════════════════════════════════════╗
    ▼                                              ║
FastAPI screener.py                                ║ Axios interceptor
    │                                              ║ normalises errors
    ▼                                              ║
GlobalResearchEngine.screen_universe()             ║
    │  For each ticker in universe:                ║
    ├── fetch_asset_data(ticker)                   ║
    │       └── yfinance.Ticker.history()          ║
    ├── calculate_composite_score(data)            ║
    │       ├── fundamental_score (30 pts)         ║
    │       ├── momentum_score    (25 pts)         ║
    │       ├── risk_adj_score    (25 pts)         ║
    │       └── macro_score       (20 pts)         ║
    └── sort by composite_score desc               ║
    │                                              ║
    ▼                                              ║
JSON response → React state → table + charts ══════╝
```

### DCA Projection (pure calculation — no network)

```
User sets $200/week, 10 years
    │
    ▼
DCASimulator.jsx
    │  GET /api/dca/scenarios?weekly_contribution=200&years=10
    ▼
GrowthProjector.project_multiple_scenarios()
    │  For each CAGR scenario:
    │  weekly_rate = (1 + annual_rate)^(1/52) - 1
    │  For each week: balance = balance*(1+r) + contribution
    │
    ▼
4 scenario projections → LineChart
```

---

## Composite Scoring System

| Component | Weight | Signals |
|-----------|--------|---------|
| **Fundamental** | 30 pts | P/E ratio, Market cap, Dividend yield |
| **Momentum** | 25 pts | 50/200-day MA crossover, 3M returns, Volume trend |
| **Risk-Adjusted** | 25 pts | Sharpe ratio, Max drawdown, Volatility |
| **Macro Alignment** | 20 pts | Trend strength, relative volume |

| Score | Rating | Action |
|-------|--------|--------|
| 80–100 | Strong Buy | Accumulate aggressively |
| 60–79  | Buy | Accumulate steadily |
| 45–59  | Hold | Maintain positions |
| 30–44  | Reduce | Scale back |
| 0–29   | Avoid | Skip |

---

## Caching Strategy

| Layer | Mechanism | TTL |
|-------|-----------|-----|
| `GlobalResearchEngine._data_cache` | In-memory dict | Session lifetime |
| `GlobalResearchEngine._score_cache` | In-memory dict | Session lifetime |
| `DCASimulator._price_cache` | In-memory dict | Session lifetime |
| React (future) | React Query / SWR | Configurable |

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/screener/universes` | List all screening universes |
| GET | `/api/screener/run` | Run screener with params |
| GET | `/api/screener/asset/{ticker}` | Single asset detail |
| GET | `/api/recommendations/weekly` | Weekly picks |
| GET | `/api/portfolio/list` | Available portfolios |
| GET | `/api/portfolio/build` | Build portfolio with live data |
| GET | `/api/dca/project` | Single growth projection |
| GET | `/api/dca/scenarios` | 4-scenario comparison |
| GET | `/api/dca/simulate` | Historical DCA backtest |
| GET | `/api/nasdaq/simulate` | Nasdaq rotation backtest |
| GET | `/api/nasdaq/universe` | Nasdaq 100 tickers |

Interactive API docs: **`/api/docs`** (Swagger UI)

---

## Technology Stack

### Backend
- **FastAPI** — async REST framework
- **Uvicorn** — ASGI server
- **Pydantic v2** — request/response validation
- **yfinance** — market data (primary)
- **pandas / numpy** — data processing

### Frontend
- **React 18** — UI library
- **Vite** — build tool with HMR
- **React Router v6** — client-side routing
- **Recharts** — chart library
- **Axios** — HTTP client
- **Lucide React** — icon library

### Testing
- **pytest** — backend unit & integration tests
- **FastAPI TestClient** — API route testing
- **Jest** — JavaScript test runner
- **React Testing Library** — component testing

---

## Security Considerations

- CORS configured — only specified origins allowed
- No API keys stored client-side
- yfinance requires no authentication
- Optional API keys (FMP, Finnhub) loaded from environment variables only
- Input validation via Pydantic on all endpoints
