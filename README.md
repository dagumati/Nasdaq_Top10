# 🌍 Global Investment Research Platform

[![GitHub](https://img.shields.io/badge/GitHub-dagumati%2FNasdaq__Top10-181717?logo=github)](https://github.com/dagumati/Nasdaq_Top10)

**A multi-agent financial research system for global equities, ETFs, and emerging markets — designed to help everyday investors build wealth through disciplined $100–$400 weekly contributions using fractional shares and dollar-cost averaging.**

> Originally built as a Nasdaq 100 rotation strategy, now expanded into a full global investment research platform.
> 📦 **Repo:** [https://github.com/dagumati/Nasdaq_Top10](https://github.com/dagumati/Nasdaq_Top10)

---

## 🗂️ Platform Overview

| Tab | Module | Description |
|-----|--------|-------------|
| 🌍 **Global Screener** | `global_research_module.py` | Screen 100+ global ETFs, thematic funds, and stocks with composite scoring |
| 💰 **Weekly Recommendations** | `global_research_module.py` | AI-generated weekly picks for your budget & risk profile |
| 🏗️ **Model Portfolios & DCA** | `weekly_dca_module.py` | Pre-built portfolios + historical DCA simulation + growth projections |
| 📊 **Nasdaq Rotation** | `nasdaq_rotation_module.py` | Original quarterly rotation strategy with benchmarks |
| 🎯 **GT/OR Asset Selector** | `gtor_selector_module.py` | Game-theory based strategic asset selector |

---

## ⚙️ Setup Instructions

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the Platform

```bash
source venv/bin/activate
python -m streamlit run app.py
```

> ⚠️ **Important:** Always use `python -m streamlit run app.py` (not `streamlit run app.py` directly).
> If you have Anaconda installed, the bare `streamlit` command may point to an outdated system
> version that fails with `ModuleNotFoundError: No module named 'streamlit.cli'`.
> Running via `python -m streamlit` ensures the active environment's version is used.

---

## 🧠 New Modules (v2.0)

### `global_research_module.py`
**GlobalResearchEngine** — Core research engine that:
- Fetches and analyzes 100+ global assets via Yahoo Finance
- Scores each asset with a 4-factor composite (0–100):
  - **Fundamentals** (P/E, market cap, dividend yield) → up to 30 pts
  - **Momentum** (MA crossovers, RSI, trend) → up to 25 pts
  - **Risk-Adjusted** (Sharpe ratio, max drawdown) → up to 25 pts
  - **Macro Alignment** (trend strength, volume) → up to 20 pts
- Generates ratings: `Strong Buy` / `Buy` / `Hold` / `Reduce` / `Avoid`
- Outputs structured JSON for dashboards and APIs

**ModelPortfolioBuilder** — 4 pre-built model portfolios:

| Portfolio | Target CAGR | Risk |
|-----------|-------------|------|
| 🌍 Global Growth | 10–15% | Medium-High |
| 🛡️ Conservative Income | 6–9% | Low-Medium |
| 🚀 Aggressive Innovation | 15–25% | High |
| 🌱 ESG & Impact | 8–12% | Medium |

### `weekly_dca_module.py`
**DCASimulator** — Historical DCA backtester:
- Simulates weekly fractional share purchases with real price data
- Tracks cost basis, unrealized gains, and CAGR per holding
- Outputs week-by-week portfolio history

**GrowthProjector** — Future compound growth calculator:
- Projects portfolio value across 4 scenarios (6%, 10%, 14%, 18% CAGR)
- Week-by-week compounding for maximum accuracy
- Handles existing balances and variable contribution sizes

### `global_research_dashboard.py`
Premium Streamlit dashboard with:
- Dark glassmorphism theme with animated cards
- Interactive Plotly charts (risk-return bubble, allocation pie, DCA growth curve)
- JSON export for API/automation pipeline integration

---

## 🌐 Investment Universes

### Thematic ETFs (10 themes, ~45 ETFs)
| Theme | Macro Tailwind | Top ETFs |
|-------|---------------|----------|
| AI & Robotics | 4th Industrial Revolution | BOTZ, ROBO, AIQ |
| Clean Energy | Net Zero transition | ICLN, TAN, FAN |
| Cybersecurity | Digital security | HACK, CIBR, BUG |
| Semiconductor | Chip supercycle | SOXX, SMH |
| Blockchain & Fintech | Financial digitization | BLOK, ARKF |
| Space & Defense | Space economy | ARKX, ITA |
| Infrastructure | Global buildout | PAVE, IFRA |
| Water & Agriculture | Resource scarcity | PHO, MOO |
| Genomics | Healthcare innovation | ARKG, XBI |
| Electric Vehicles | Transportation electrification | DRIV, LIT |

### Global & Regional ETFs (~50 ETFs)
- US Broad Market, Developed International, Emerging Markets
- India, China, Latin America, Southeast Asia, Frontier Markets
- Bonds, Real Estate, Commodities

### Global Growth Stocks (~60 stocks)
- US Tech Leaders, US Innovation, Healthcare, Fintech
- International ADRs (TSM, ASML, MELI, NVO), Dividend Aristocrats

---

## � Weekly DCA Strategy Guide

For a **$200/week** budget at **10% expected CAGR**:

| Years | Total Contributed | Portfolio Value | Growth |
|-------|-------------------|-----------------|--------|
| 1     | $10,400           | $10,923          | +5.2%  |
| 5     | $52,000           | $67,200          | +29%   |
| 10    | $104,000          | $177,000         | +70%   |
| 20    | $208,000          | $638,000         | +207%  |

> *Compound interest at work — the last 10 years generate more growth than the first 10.*

---

## 📊 Composite Scoring System

```
Score   Rating        Action
80–100  Strong Buy    Accumulate aggressively via DCA
60–79   Buy           Accumulate steadily
45–59   Hold          Maintain; pause new contributions
30–44   Reduce        Scale back; rebalance toward stronger assets
0–29    Avoid         Skip; better opportunities elsewhere
```

---

## � JSON Output for API Integration

Every recommendation and portfolio can be exported as structured JSON:

```json
{
  "generated_at": "2026-02-24T19:00:00",
  "weekly_budget": 200,
  "risk_profile": "Moderate",
  "recommendations": [
    {
      "bucket": "US Core",
      "ticker": "VTI",
      "weekly_amount": 35.00,
      "fractional_shares": 0.1654,
      "composite_score": 72.5,
      "rating": "Buy",
      "reason": "VTI scores 72.5/100..."
    }
  ]
}
```

---

## 🔧 Troubleshooting

```bash
# Re-create virtual environment
rm -rf venv && python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Always run with python -m to use the active environment's streamlit
python -m streamlit run app.py
```

### "No module named 'streamlit.cli'" Error

This happens when `streamlit` on your PATH points to an old Anaconda installation.
**Fix:** Always prefix with `python -m`:

```bash
python -m streamlit run app.py
```

---

## ⚠️ Disclaimer

These tools are for **educational purposes only**. Past performance does not guarantee future results. This platform does not constitute financial advice. Always do your own research before investing.

---

## 🆕 Changelog

### v2.0 — Global Investment Research Platform
- ✅ **Global Market Screener** — 100+ assets, composite scoring
- ✅ **Weekly Recommendations** — budget-driven, risk-profile-aware
- ✅ **4 Model Portfolios** — Global Growth, Conservative, Aggressive, ESG
- ✅ **DCA Simulator** — historical backtest with real weekly price data
- ✅ **Compound Growth Projector** — 4 scenarios, week-by-week compounding
- ✅ **JSON Export** — structured output for APIs and dashboard pipelines
- ✅ **Premium Dark UI** — glassmorphism theme, animated cards, interactive charts

### v1.0 — Nasdaq Rotation Strategy
- ✅ Quarterly Nasdaq 100 rotation with top-10 market cap selection
- ✅ Multi-API support (Yahoo Finance, FMP, Finnhub, Alpha Vantage, Polygon)
- ✅ GT/OR Strategic Asset Selector with SVI scoring
- ✅ Benchmark comparison (QQQ, SPY)
