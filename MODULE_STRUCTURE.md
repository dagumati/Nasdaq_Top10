# Module Structure — Global Investment Research Platform v2.0

---

## Backend Modules (FastAPI)

### `backend/main.py`
- App factory with CORS, lifespan hooks, and router registration
- Health endpoints: `GET /` and `GET /api/health`
- Global exception handler with structured JSON error responses

### `backend/models/schemas.py`
- Pydantic v2 request/response models for all endpoints
- Enums: `RiskProfile`, `UniverseType`, `PortfolioName`
- Enforces validation (min/max budget, valid risk profiles, etc.)

### `backend/routers/screener.py`
- `GET /api/screener/universes` — lists all universes + counts
- `GET /api/screener/run` — screens a universe, returns ranked assets
- `GET /api/screener/asset/{ticker}` — detailed single-asset analysis

### `backend/routers/recommendations.py`
- `GET /api/recommendations/weekly` — AI-generated weekly buy picks
- `GET /api/recommendations/weekly/json` — same, as raw JSON string

### `backend/routers/portfolio.py`
- `GET /api/portfolio/list` — template metadata (no live data)
- `GET /api/portfolio/build` — live-scored portfolio holdings

### `backend/routers/dca.py`
- `GET /api/dca/project` — single compound growth curve
- `GET /api/dca/scenarios` — 4 CAGR scenarios side-by-side
- `GET /api/dca/simulate` — historical DCA backtest

### `backend/routers/nasdaq.py`
- `GET /api/nasdaq/simulate` — quarterly rotation backtest
- `GET /api/nasdaq/universe` — list of Nasdaq 100 tickers

---

## Core Python Modules

### `global_research_module.py`
**`GlobalResearchEngine`**
- `fetch_asset_data(ticker, period)` → dict of price, returns, fundamentals
- `calculate_composite_score(data)` → 4-component score object
- `screen_universe(universe, top_n)` → sorted list of scored assets
- `generate_weekly_recommendations(budget, risk_profile)` → recommendation dict
- Internal caches: `_data_cache`, `_score_cache`

**`ModelPortfolioBuilder`**
- `PORTFOLIO_TEMPLATES` — 4 portfolio definitions (Global Growth, Conservative, Aggressive, ESG)
- `build_portfolio_with_live_data(name, weekly_budget)` → live-scored holdings
- `get_portfolio_names()` → list of portfolio names

**Universe Definitions**
- `THEMATIC_ETF_UNIVERSE` — 10 themes × ~4–6 ETFs each
- `GLOBAL_ETF_UNIVERSE` — regional/asset-class ETFs
- `GLOBAL_GROWTH_STOCKS` — categorized individual stocks

**`export_recommendations_json(recommendations)`** → JSON string for APIs

---

### `weekly_dca_module.py`
**`DCASimulator`**
- `simulate_dca(portfolio, weekly_budget, start_date, end_date)` → full backtest
- `_fetch_weekly_prices(ticker, start, end)` → cached price fetch
- `_price_cache` — in-memory price cache

**`GrowthProjector`**
- `project_growth(weekly_contribution, expected_annual_return, years, existing_balance)` → projection dict
- `project_multiple_scenarios(weekly_contribution, years, existing_balance)` → 4-scenario dict

---

### `nasdaq_rotation_module.py`
- `OptimizedYahooDataFetcher` — fetches Nasdaq 100 data with retry logic
- `OptimizedPortfolioSimulator` — quarterly rotation simulation

### `nasdaq_rotation_dashboard.py`
- Streamlit tab: portfolio metrics, performance charts, benchmark comparison

### `global_research_dashboard.py`
- Three Streamlit tabs: Global Screener, Weekly Recommendations, Model Portfolios
- Premium dark CSS theme, Plotly charts

### `gtor_selector_module.py`
- GT/OR (Game Theory / Operations Research) asset selection algorithm
- SVI (Strategic Value Index) scoring

---

## Frontend Modules (React)

### `src/services/api.js`
- Axios instance with timeout (120s) and interceptors
- `screenerApi`, `recommendationsApi`, `portfolioApi`, `dcaApi`, `nasdaqApi`, `healthApi`

### `src/hooks/useApi.js`
- `useApi(apiFn)` → `{ data, loading, error, execute, reset }`

### `src/context/ThemeContext.jsx`
- `ThemeProvider` — persists to localStorage, respects `prefers-color-scheme`
- `useTheme()` → `{ theme, toggle }`

### `src/components/Layout/`
- `Layout.jsx` — shell with health check on mount
- `Sidebar.jsx` — fixed nav with `NavLink` active states
- `Navbar.jsx` — page title, theme toggle, API status pill

### `src/components/Cards/`
- `MetricCard.jsx` — KPI with label, value, delta, optional icon
- `SharedUI.jsx` — `RatingBadge`, `Loading`, `ErrorAlert`, `SectionHeader`, `ScoreBar`, `formatCurrency`, `formatPct`, `ColoredPct`

### `src/components/Tables/`
- `ScreenerTable.jsx` — sortable table with score bars, rating badges, colored returns

### `src/pages/`
| File | Route | Features |
|------|-------|---------|
| `Dashboard.jsx` | `/` | Hero, API health, feature cards |
| `GlobalScreener.jsx` | `/screener` | Universe picker, table, radar, scatter |
| `WeeklyRecommendations.jsx` | `/recommendations` | Budget slider, risk profile, pie, cards |
| `ModelPortfolios.jsx` | `/portfolios` | Portfolio picker, holdings table, pie |
| `DCASimulator.jsx` | `/dca` | Growth projection, backtest, area chart |
| `NasdaqRotation.jsx` | `/nasdaq` | Simulation config, line chart, bar chart |

---

## Tests

### `backend/tests/test_api.py`
- `TestHealth` — root and health endpoints
- `TestScreener` — universe listing, run, validation, sort order
- `TestRecommendations` — weekly picks, invalid profile, budget bounds
- `TestPortfolio` — list, build, validation
- `TestDCA` — projection math, scenario ordering, simulate validation
- `TestNasdaq` — date validation

### `frontend/src/__tests__/`
- `MetricCard.test.jsx` — render, delta, no-delta
- `SharedUI.test.jsx` — RatingBadge classes, ScoreBar fill, formatters
- `useApi.test.js` — loading, success, error, reset, argument passing
