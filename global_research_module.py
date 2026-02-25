"""
Global Investment Research Module
=================================
Multi-agent financial research engine for global equities, ETFs, and emerging markets.
Designed to help everyday investors who contribute $100-$400 weekly into diversified
portfolios using fractional shares and recurring investments.

Core capabilities:
- Global market research beyond Nasdaq
- Emerging/frontier market screening
- Thematic ETF identification
- Fundamental scoring & ranking
- Macro signal integration
- Structured JSON output for dashboards/APIs
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# UNIVERSE DEFINITIONS
# ============================================================================

# Thematic ETF Universe — organized by investment theme
THEMATIC_ETF_UNIVERSE = {
    "AI & Robotics": {
        "tickers": ["BOTZ", "ROBO", "IRBO", "AIQ", "ARKQ"],
        "description": "Artificial intelligence, robotics, and automation",
        "macro_theme": "Fourth Industrial Revolution"
    },
    "Clean Energy": {
        "tickers": ["ICLN", "QCLN", "TAN", "FAN", "PBW"],
        "description": "Solar, wind, and clean energy transition",
        "macro_theme": "Energy Transition & Net Zero"
    },
    "Cybersecurity": {
        "tickers": ["HACK", "CIBR", "BUG", "IHAK"],
        "description": "Cybersecurity infrastructure and services",
        "macro_theme": "Digital Security"
    },
    "Genomics & Biotech": {
        "tickers": ["ARKG", "XBI", "IBB", "GNOM"],
        "description": "Genomics, CRISPR, and biotechnology innovation",
        "macro_theme": "Healthcare Innovation"
    },
    "Semiconductor": {
        "tickers": ["SOXX", "SMH", "PSI", "SOXQ"],
        "description": "Semiconductor manufacturing and design",
        "macro_theme": "Chip Supercycle"
    },
    "Blockchain & Fintech": {
        "tickers": ["BLOK", "ARKF", "FINX", "IPAY"],
        "description": "Blockchain, fintech, and digital payments",
        "macro_theme": "Financial Digitization"
    },
    "Space & Defense": {
        "tickers": ["ARKX", "UFO", "ITA", "PPA"],
        "description": "Space exploration and defense technology",
        "macro_theme": "Space Economy"
    },
    "Infrastructure": {
        "tickers": ["PAVE", "IFRA", "NFRA", "IGF"],
        "description": "Infrastructure spending and development",
        "macro_theme": "Global Infrastructure Buildout"
    },
    "Water & Agriculture": {
        "tickers": ["PHO", "FIW", "MOO", "VEGI"],
        "description": "Water resources and agricultural technology",
        "macro_theme": "Resource Scarcity"
    },
    "Electric Vehicles": {
        "tickers": ["DRIV", "IDRV", "LIT", "KARS"],
        "description": "Electric vehicles and battery technology",
        "macro_theme": "Transportation Electrification"
    }
}

# Global & Regional ETF Universe
GLOBAL_ETF_UNIVERSE = {
    "US Broad Market": {
        "tickers": ["VTI", "SPY", "QQQ", "IWM", "DIA"],
        "region": "United States",
        "risk_level": "Medium"
    },
    "Developed International": {
        "tickers": ["VEA", "EFA", "IEFA", "VGK", "EWJ"],
        "region": "Europe, Japan, Australia",
        "risk_level": "Medium"
    },
    "Emerging Markets": {
        "tickers": ["VWO", "EEM", "IEMG", "SCHE"],
        "region": "China, India, Brazil, etc.",
        "risk_level": "High"
    },
    "India": {
        "tickers": ["INDA", "INDY", "SMIN", "EPI"],
        "region": "India",
        "risk_level": "High"
    },
    "China": {
        "tickers": ["MCHI", "FXI", "KWEB", "CQQQ"],
        "region": "China",
        "risk_level": "High"
    },
    "Latin America": {
        "tickers": ["ILF", "EWZ", "EWW"],
        "region": "Brazil, Mexico, etc.",
        "risk_level": "High"
    },
    "Southeast Asia": {
        "tickers": ["ASEA", "VNM", "EIDO", "THD"],
        "region": "Vietnam, Indonesia, Thailand",
        "risk_level": "High"
    },
    "Frontier Markets": {
        "tickers": ["FM", "FRN"],
        "region": "Nigeria, Kenya, Bangladesh, etc.",
        "risk_level": "Very High"
    },
    "Bonds & Fixed Income": {
        "tickers": ["BND", "AGG", "TLT", "BNDX", "EMB"],
        "region": "Global",
        "risk_level": "Low"
    },
    "Real Estate": {
        "tickers": ["VNQ", "VNQI", "REM", "REET"],
        "region": "Global",
        "risk_level": "Medium"
    },
    "Commodities": {
        "tickers": ["GLD", "SLV", "DBA", "DBC", "USO"],
        "region": "Global",
        "risk_level": "High"
    }
}

# High-Growth Global Stocks (beyond Nasdaq)
GLOBAL_GROWTH_STOCKS = {
    "US Tech Leaders": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "CRM", "AMD"],
    "US Innovation": ["PLTR", "SNOW", "DDOG", "NET", "CRWD", "ZS", "MDB", "TEAM", "PANW", "FTNT"],
    "Healthcare Innovation": ["LLY", "UNH", "JNJ", "ABBV", "TMO", "ISRG", "DXCM", "VEEV", "HIMS", "DOCS"],
    "Fintech & Payments": ["V", "MA", "SQ", "PYPL", "COIN", "SOFI", "AFRM", "NU", "GRAB"],
    "International ADRs": ["TSM", "ASML", "NVO", "SAP", "SHOP", "MELI", "SE", "BABA", "PDD", "GRAB"],
    "Dividend Aristocrats": ["PG", "KO", "PEP", "JNJ", "MMM", "ABT", "MCD", "WMT", "HD", "COST"],
}


# ============================================================================
# GLOBAL RESEARCH ENGINE
# ============================================================================

class GlobalResearchEngine:
    """
    Multi-agent global market research engine.
    Analyzes equities, ETFs, and emerging markets for weekly investment recommendations.
    """

    def __init__(self):
        self._data_cache = {}
        self._score_cache = {}
        self._analysis_timestamp = None

    def fetch_asset_data(self, ticker: str, period: str = "1y") -> Optional[Dict]:
        """Fetch comprehensive data for a single asset"""
        cache_key = f"{ticker}_{period}"
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]

        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                return None

            info = {}
            try:
                info = stock.info or {}
            except Exception:
                pass

            # Calculate key metrics
            returns = hist['Close'].pct_change().dropna()
            current_price = hist['Close'].iloc[-1] if len(hist) > 0 else 0

            data = {
                "ticker": ticker,
                "name": info.get("shortName", info.get("longName", ticker)),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "country": info.get("country", "N/A"),
                "current_price": round(float(current_price), 2),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "forward_pe": info.get("forwardPE", None),
                "dividend_yield": info.get("dividendYield", 0) or 0,
                "beta": info.get("beta", 1.0) or 1.0,
                "52w_high": info.get("fiftyTwoWeekHigh", 0),
                "52w_low": info.get("fiftyTwoWeekLow", 0),
                "avg_volume": info.get("averageVolume", 0),
                "history": hist,
                "returns": returns,
                # Calculated metrics
                "return_1m": self._calc_period_return(hist, 21),
                "return_3m": self._calc_period_return(hist, 63),
                "return_6m": self._calc_period_return(hist, 126),
                "return_1y": self._calc_period_return(hist, 252),
                "volatility_30d": float(returns.tail(30).std() * np.sqrt(252) * 100) if len(returns) >= 30 else 0,
                "sharpe_ratio": self._calc_sharpe(returns),
                "max_drawdown": self._calc_max_drawdown(hist['Close']),
                "momentum_score": self._calc_momentum_score(hist),
                "trend_strength": self._calc_trend_strength(hist),
                "volume_trend": self._calc_volume_trend(hist),
            }

            self._data_cache[cache_key] = data
            return data

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None

    def _calc_period_return(self, hist: pd.DataFrame, days: int) -> float:
        """Calculate return over a specific period"""
        if len(hist) < days:
            return 0.0
        return float((hist['Close'].iloc[-1] / hist['Close'].iloc[-days] - 1) * 100)

    def _calc_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.05) -> float:
        """Calculate annualized Sharpe ratio"""
        if len(returns) < 30:
            return 0.0
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0.0
        return float((excess_returns.mean() / excess_returns.std()) * np.sqrt(252))

    def _calc_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown percentage"""
        peak = prices.expanding(min_periods=1).max()
        drawdown = (prices - peak) / peak
        return float(drawdown.min() * 100)

    def _calc_momentum_score(self, hist: pd.DataFrame) -> float:
        """Calculate composite momentum score (0-100)"""
        if len(hist) < 200:
            return 50.0

        close = hist['Close']
        score = 0

        # Price above 50-day MA
        ma50 = close.rolling(50).mean().iloc[-1]
        if close.iloc[-1] > ma50:
            score += 25

        # Price above 200-day MA
        ma200 = close.rolling(200).mean().iloc[-1]
        if close.iloc[-1] > ma200:
            score += 25

        # 50-day MA above 200-day MA (golden cross)
        if ma50 > ma200:
            score += 20

        # Positive 3-month return
        ret_3m = (close.iloc[-1] / close.iloc[-63] - 1) if len(close) >= 63 else 0
        if ret_3m > 0:
            score += 15

        # RSI between 40-70 (healthy momentum, not overbought)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain.iloc[-1] / loss.iloc[-1] if loss.iloc[-1] != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        if 40 <= rsi <= 70:
            score += 15

        return float(score)

    def _calc_trend_strength(self, hist: pd.DataFrame) -> str:
        """Classify trend strength"""
        if len(hist) < 200:
            return "Insufficient Data"

        close = hist['Close']
        ma50 = close.rolling(50).mean().iloc[-1]
        ma200 = close.rolling(200).mean().iloc[-1]
        current = close.iloc[-1]

        if current > ma50 > ma200:
            return "Strong Uptrend"
        elif current > ma200 and current < ma50:
            return "Weakening Uptrend"
        elif current < ma50 < ma200:
            return "Strong Downtrend"
        elif current < ma200 and current > ma50:
            return "Weakening Downtrend"
        else:
            return "Sideways"

    def _calc_volume_trend(self, hist: pd.DataFrame) -> str:
        """Analyze volume trend"""
        if len(hist) < 50:
            return "N/A"

        vol_20 = hist['Volume'].tail(20).mean()
        vol_50 = hist['Volume'].tail(50).mean()

        ratio = vol_20 / vol_50 if vol_50 > 0 else 1

        if ratio > 1.3:
            return "Surging"
        elif ratio > 1.1:
            return "Increasing"
        elif ratio > 0.9:
            return "Stable"
        elif ratio > 0.7:
            return "Declining"
        else:
            return "Very Low"

    # ========================================================================
    # SCORING & RANKING
    # ========================================================================

    def calculate_composite_score(self, data: Dict) -> Dict:
        """
        Calculate a composite investment score (0-100) based on:
        - Fundamentals (30%)
        - Momentum (25%)
        - Risk-Adjusted Returns (25%)
        - Macro Alignment (20%)
        """
        scores = {}

        # --- Fundamental Score (0-30) ---
        fund_score = 0
        pe = data.get("forward_pe") or data.get("pe_ratio")
        if pe and pe > 0:
            if pe < 15:
                fund_score += 10
            elif pe < 25:
                fund_score += 7
            elif pe < 40:
                fund_score += 4
            else:
                fund_score += 1

        # Market cap stability
        mcap = data.get("market_cap", 0)
        if mcap > 100e9:
            fund_score += 10  # Mega cap
        elif mcap > 10e9:
            fund_score += 8   # Large cap
        elif mcap > 2e9:
            fund_score += 5   # Mid cap
        elif mcap > 300e6:
            fund_score += 3   # Small cap
        else:
            fund_score += 1

        # Dividend bonus
        div_yield = data.get("dividend_yield", 0)
        if div_yield > 0.03:
            fund_score += 10
        elif div_yield > 0.01:
            fund_score += 7
        elif div_yield > 0:
            fund_score += 4

        scores["fundamental"] = min(fund_score, 30)

        # --- Momentum Score (0-25) ---
        momentum = data.get("momentum_score", 50)
        scores["momentum"] = round(momentum * 0.25, 1)

        # --- Risk-Adjusted Score (0-25) ---
        risk_score = 0
        sharpe = data.get("sharpe_ratio", 0)
        if sharpe > 2:
            risk_score += 15
        elif sharpe > 1:
            risk_score += 12
        elif sharpe > 0.5:
            risk_score += 8
        elif sharpe > 0:
            risk_score += 4

        max_dd = abs(data.get("max_drawdown", 0))
        if max_dd < 10:
            risk_score += 10
        elif max_dd < 20:
            risk_score += 7
        elif max_dd < 30:
            risk_score += 4
        else:
            risk_score += 1

        scores["risk_adjusted"] = min(risk_score, 25)

        # --- Macro Alignment Score (0-20) ---
        macro_score = 0
        trend = data.get("trend_strength", "")
        if "Strong Uptrend" in str(trend):
            macro_score += 10
        elif "Weakening Uptrend" in str(trend):
            macro_score += 5

        vol_trend = data.get("volume_trend", "")
        if vol_trend in ["Surging", "Increasing"]:
            macro_score += 10
        elif vol_trend == "Stable":
            macro_score += 5

        scores["macro_alignment"] = min(macro_score, 20)

        # --- Composite ---
        composite = sum(scores.values())
        scores["composite"] = round(composite, 1)

        # --- Rating ---
        if composite >= 75:
            scores["rating"] = "Strong Buy"
            scores["confidence"] = "High"
        elif composite >= 60:
            scores["rating"] = "Buy"
            scores["confidence"] = "Medium-High"
        elif composite >= 45:
            scores["rating"] = "Hold"
            scores["confidence"] = "Medium"
        elif composite >= 30:
            scores["rating"] = "Reduce"
            scores["confidence"] = "Medium-Low"
        else:
            scores["rating"] = "Avoid"
            scores["confidence"] = "Low"

        return scores

    def screen_universe(self, universe: Dict[str, List[str]], top_n: int = 10,
                        progress_callback=None) -> List[Dict]:
        """
        Screen an entire universe of assets and return ranked results.
        """
        all_results = []
        all_tickers = []

        # Flatten the universe
        for category, tickers in universe.items():
            if isinstance(tickers, dict) and "tickers" in tickers:
                for t in tickers["tickers"]:
                    all_tickers.append((t, category))
            elif isinstance(tickers, list):
                for t in tickers:
                    all_tickers.append((t, category))

        total = len(all_tickers)

        for idx, (ticker, category) in enumerate(all_tickers):
            if progress_callback:
                progress_callback(idx / total, f"Analyzing {ticker} ({idx+1}/{total})...")

            data = self.fetch_asset_data(ticker, period="1y")
            if data is None:
                continue

            scores = self.calculate_composite_score(data)

            result = {
                "ticker": ticker,
                "name": data["name"],
                "category": category,
                "sector": data["sector"],
                "country": data["country"],
                "current_price": data["current_price"],
                "market_cap": data["market_cap"],
                "return_1m": round(data["return_1m"], 2),
                "return_3m": round(data["return_3m"], 2),
                "return_6m": round(data["return_6m"], 2),
                "return_1y": round(data["return_1y"], 2),
                "volatility_30d": round(data["volatility_30d"], 2),
                "sharpe_ratio": round(data["sharpe_ratio"], 2),
                "max_drawdown": round(data["max_drawdown"], 2),
                "momentum_score": round(data["momentum_score"], 1),
                "trend_strength": data["trend_strength"],
                "volume_trend": data["volume_trend"],
                "composite_score": scores["composite"],
                "rating": scores["rating"],
                "confidence": scores["confidence"],
                "fundamental_score": scores["fundamental"],
                "momentum_sub_score": scores["momentum"],
                "risk_adjusted_score": scores["risk_adjusted"],
                "macro_alignment_score": scores["macro_alignment"],
            }

            all_results.append(result)

        # Sort by composite score
        all_results.sort(key=lambda x: x["composite_score"], reverse=True)

        if progress_callback:
            progress_callback(1.0, "Analysis complete!")

        return all_results[:top_n]

    # ========================================================================
    # WEEKLY RECOMMENDATION ENGINE
    # ========================================================================

    def generate_weekly_recommendations(self, weekly_budget: float = 200.0,
                                        risk_profile: str = "Moderate",
                                        progress_callback=None) -> Dict:
        """
        Generate weekly investment recommendations for a given budget.

        Args:
            weekly_budget: Amount to invest per week ($100-$400)
            risk_profile: "Conservative", "Moderate", or "Aggressive"

        Returns:
            Structured recommendation dict with allocations and reasoning.
        """

        # Define allocation targets based on risk profile
        allocation_targets = {
            "Conservative": {
                "US Core": 0.40,
                "International Developed": 0.15,
                "Bonds & Fixed Income": 0.20,
                "Thematic Growth": 0.10,
                "Emerging Markets": 0.05,
                "Commodities": 0.10,
            },
            "Moderate": {
                "US Core": 0.35,
                "International Developed": 0.15,
                "Thematic Growth": 0.20,
                "Emerging Markets": 0.10,
                "Bonds & Fixed Income": 0.10,
                "Commodities": 0.10,
            },
            "Aggressive": {
                "US Core": 0.25,
                "Thematic Growth": 0.30,
                "Emerging Markets": 0.15,
                "International Developed": 0.15,
                "Individual Growth Stocks": 0.10,
                "Commodities": 0.05,
            }
        }

        targets = allocation_targets.get(risk_profile, allocation_targets["Moderate"])

        # Map allocation buckets to specific ETFs/Stocks
        bucket_to_tickers = {
            "US Core": ["VTI", "QQQ", "SPY"],
            "International Developed": ["VEA", "EFA", "VGK"],
            "Thematic Growth": ["BOTZ", "ICLN", "SOXX", "HACK", "PAVE"],
            "Emerging Markets": ["VWO", "INDA", "EEM"],
            "Bonds & Fixed Income": ["BND", "AGG", "TLT"],
            "Commodities": ["GLD", "SLV", "DBA"],
            "Individual Growth Stocks": ["NVDA", "PLTR", "MELI", "NU", "TSM"],
        }

        recommendations = []
        total_tickers = sum(len(v) for k, v in bucket_to_tickers.items() if k in targets)
        processed = 0

        for bucket, weight in targets.items():
            bucket_amount = round(weekly_budget * weight, 2)
            tickers = bucket_to_tickers.get(bucket, [])

            if not tickers:
                continue

            bucket_results = []
            for ticker in tickers[:3]:  # Top 3 per bucket
                processed += 1
                if progress_callback:
                    progress_callback(processed / total_tickers,
                                      f"Screening {ticker} for {bucket}...")

                data = self.fetch_asset_data(ticker, period="6mo")
                if data is None:
                    continue

                scores = self.calculate_composite_score(data)
                bucket_results.append({
                    "ticker": ticker,
                    "name": data["name"],
                    "price": data["current_price"],
                    "composite_score": scores["composite"],
                    "rating": scores["rating"],
                    "return_3m": round(data["return_3m"], 2),
                    "volatility": round(data["volatility_30d"], 2),
                    "trend": data["trend_strength"],
                })

            # Sort by composite score within bucket
            bucket_results.sort(key=lambda x: x["composite_score"], reverse=True)

            # Allocate within bucket — best asset gets 50%, second 30%, third 20%
            allocation_splits = [0.50, 0.30, 0.20]
            for i, asset in enumerate(bucket_results):
                if i >= len(allocation_splits):
                    break
                alloc_amount = round(bucket_amount * allocation_splits[i], 2)
                fractional_shares = round(alloc_amount / asset["price"], 6) if asset["price"] > 0 else 0

                recommendations.append({
                    "bucket": bucket,
                    "ticker": asset["ticker"],
                    "name": asset["name"],
                    "allocation_pct": round(weight * allocation_splits[i] * 100, 1),
                    "weekly_amount": alloc_amount,
                    "current_price": asset["price"],
                    "fractional_shares": fractional_shares,
                    "composite_score": asset["composite_score"],
                    "rating": asset["rating"],
                    "return_3m": asset["return_3m"],
                    "volatility": asset["volatility"],
                    "trend": asset["trend"],
                    "reason": self._generate_reason(asset, bucket)
                })

        if progress_callback:
            progress_callback(1.0, "Recommendations ready!")

        # Build structured output
        output = {
            "generated_at": datetime.now().isoformat(),
            "weekly_budget": weekly_budget,
            "risk_profile": risk_profile,
            "total_positions": len(recommendations),
            "allocation_summary": targets,
            "recommendations": recommendations,
            "portfolio_metrics": self._calc_portfolio_metrics(recommendations),
            "disclaimer": (
                "These recommendations are for educational purposes only. "
                "Past performance does not guarantee future results. "
                "Always do your own research before investing."
            )
        }

        return output

    def _generate_reason(self, asset: Dict, bucket: str) -> str:
        """Generate a clear explanation for each recommendation"""
        ticker = asset["ticker"]
        score = asset["composite_score"]
        trend = asset["trend"]
        ret_3m = asset["return_3m"]

        reasons = []

        if score >= 70:
            reasons.append(f"{ticker} scores {score}/100 — strong across fundamentals, momentum, and risk metrics.")
        elif score >= 50:
            reasons.append(f"{ticker} scores {score}/100 — solid profile with room for improvement.")
        else:
            reasons.append(f"{ticker} scores {score}/100 — included for diversification within {bucket}.")

        if "Uptrend" in str(trend):
            reasons.append(f"Currently in a {trend.lower()}, favoring accumulation.")
        elif "Downtrend" in str(trend):
            reasons.append(f"Currently in a {trend.lower()} — dollar-cost averaging helps reduce average cost.")

        if ret_3m > 10:
            reasons.append(f"Strong 3-month return of {ret_3m}% reflects positive momentum.")
        elif ret_3m < -10:
            reasons.append(f"3-month decline of {ret_3m}% may offer value entry via DCA.")

        return " ".join(reasons)

    def _calc_portfolio_metrics(self, recommendations: List[Dict]) -> Dict:
        """Calculate aggregate portfolio metrics from recommendations"""
        if not recommendations:
            return {}

        total_amount = sum(r["weekly_amount"] for r in recommendations)
        weighted_score = sum(r["composite_score"] * r["weekly_amount"] for r in recommendations) / total_amount if total_amount > 0 else 0
        weighted_vol = sum(r["volatility"] * r["weekly_amount"] for r in recommendations) / total_amount if total_amount > 0 else 0

        buckets = set(r["bucket"] for r in recommendations)

        return {
            "total_weekly_investment": round(total_amount, 2),
            "weighted_composite_score": round(weighted_score, 1),
            "weighted_volatility": round(weighted_vol, 1),
            "num_positions": len(recommendations),
            "num_buckets": len(buckets),
            "diversification_score": min(100, len(buckets) * 15),
        }


# ============================================================================
# MODEL PORTFOLIO BUILDER
# ============================================================================

class ModelPortfolioBuilder:
    """
    Builds and maintains model portfolios optimized for:
    - Long-term compounding
    - Sector diversification
    - Volatility control
    - Dollar-cost averaging
    """

    PORTFOLIO_TEMPLATES = {
        "🌍 Global Growth": {
            "description": "Diversified global growth across US, international, and emerging markets",
            "target_return": "10-15% CAGR",
            "risk_level": "Medium-High",
            "holdings": {
                "VTI": {"weight": 0.25, "role": "US Total Market Core"},
                "QQQ": {"weight": 0.15, "role": "US Tech & Innovation"},
                "VEA": {"weight": 0.10, "role": "Developed International"},
                "VWO": {"weight": 0.10, "role": "Emerging Markets Broad"},
                "INDA": {"weight": 0.05, "role": "India Growth"},
                "SOXX": {"weight": 0.10, "role": "Semiconductor Theme"},
                "ICLN": {"weight": 0.05, "role": "Clean Energy Theme"},
                "BND": {"weight": 0.10, "role": "Bond Stabilizer"},
                "GLD": {"weight": 0.05, "role": "Inflation Hedge"},
                "PAVE": {"weight": 0.05, "role": "Infrastructure Theme"},
            }
        },
        "🛡️ Conservative Income": {
            "description": "Income-focused with downside protection for cautious investors",
            "target_return": "6-9% CAGR",
            "risk_level": "Low-Medium",
            "holdings": {
                "VTI": {"weight": 0.20, "role": "US Total Market Core"},
                "VEA": {"weight": 0.10, "role": "International Developed"},
                "BND": {"weight": 0.25, "role": "US Bond Core"},
                "BNDX": {"weight": 0.10, "role": "International Bonds"},
                "VNQ": {"weight": 0.10, "role": "Real Estate Income"},
                "GLD": {"weight": 0.10, "role": "Gold Hedge"},
                "AGG": {"weight": 0.10, "role": "Aggregate Bond Fund"},
                "EMB": {"weight": 0.05, "role": "Emerging Market Bonds"},
            }
        },
        "🚀 Aggressive Innovation": {
            "description": "High-growth focus on disruptive themes and emerging markets",
            "target_return": "15-25% CAGR (with higher volatility)",
            "risk_level": "High",
            "holdings": {
                "QQQ": {"weight": 0.15, "role": "Nasdaq 100 Core"},
                "SOXX": {"weight": 0.12, "role": "Semiconductor Supercycle"},
                "BOTZ": {"weight": 0.10, "role": "AI & Robotics"},
                "HACK": {"weight": 0.08, "role": "Cybersecurity"},
                "ICLN": {"weight": 0.08, "role": "Clean Energy"},
                "INDA": {"weight": 0.08, "role": "India Growth Story"},
                "VWO": {"weight": 0.07, "role": "Broad Emerging Markets"},
                "ARKF": {"weight": 0.07, "role": "Fintech Innovation"},
                "LIT": {"weight": 0.07, "role": "EV & Battery Tech"},
                "KWEB": {"weight": 0.05, "role": "China Internet"},
                "VNM": {"weight": 0.05, "role": "Vietnam Frontier"},
                "GLD": {"weight": 0.05, "role": "Gold Hedge"},
                "FM": {"weight": 0.03, "role": "Frontier Markets"},
            }
        },
        "🌱 ESG & Impact": {
            "description": "Sustainable investing focused on Environmental, Social, and Governance themes",
            "target_return": "8-12% CAGR",
            "risk_level": "Medium",
            "holdings": {
                "VTI": {"weight": 0.20, "role": "US Total Market Core"},
                "ICLN": {"weight": 0.12, "role": "Clean Energy"},
                "TAN": {"weight": 0.08, "role": "Solar Energy"},
                "FAN": {"weight": 0.05, "role": "Wind Energy"},
                "PHO": {"weight": 0.08, "role": "Water Resources"},
                "PAVE": {"weight": 0.08, "role": "Sustainable Infrastructure"},
                "VEA": {"weight": 0.10, "role": "International Developed"},
                "VWO": {"weight": 0.07, "role": "Emerging Markets"},
                "BND": {"weight": 0.12, "role": "Bond Stabilizer"},
                "GLD": {"weight": 0.05, "role": "Inflation Hedge"},
                "MOO": {"weight": 0.05, "role": "Sustainable Agriculture"},
            }
        }
    }

    def __init__(self, research_engine: GlobalResearchEngine):
        self.engine = research_engine

    def get_portfolio_names(self) -> List[str]:
        return list(self.PORTFOLIO_TEMPLATES.keys())

    def get_portfolio_template(self, name: str) -> Dict:
        return self.PORTFOLIO_TEMPLATES.get(name, {})

    def build_portfolio_with_live_data(self, portfolio_name: str,
                                       weekly_budget: float = 200.0,
                                       progress_callback=None) -> Dict:
        """Build a model portfolio with live market data and weekly allocation"""
        template = self.PORTFOLIO_TEMPLATES.get(portfolio_name)
        if not template:
            return {"error": f"Portfolio '{portfolio_name}' not found"}

        holdings = template["holdings"]
        results = []
        total = len(holdings)

        for idx, (ticker, config) in enumerate(holdings.items()):
            if progress_callback:
                progress_callback(idx / total, f"Fetching {ticker}...")

            data = self.engine.fetch_asset_data(ticker, period="6mo")
            if data is None:
                continue

            scores = self.engine.calculate_composite_score(data)
            weekly_amount = round(weekly_budget * config["weight"], 2)
            fractional = round(weekly_amount / data["current_price"], 6) if data["current_price"] > 0 else 0

            results.append({
                "ticker": ticker,
                "name": data["name"],
                "role": config["role"],
                "weight_pct": round(config["weight"] * 100, 1),
                "weekly_amount": weekly_amount,
                "fractional_shares": fractional,
                "current_price": data["current_price"],
                "return_3m": round(data["return_3m"], 2),
                "return_6m": round(data["return_6m"], 2),
                "volatility_30d": round(data["volatility_30d"], 2),
                "sharpe_ratio": round(data["sharpe_ratio"], 2),
                "max_drawdown": round(data["max_drawdown"], 2),
                "composite_score": scores["composite"],
                "rating": scores["rating"],
                "trend_strength": data["trend_strength"],
            })

        if progress_callback:
            progress_callback(1.0, "Portfolio built!")

        # Calculate portfolio-level metrics
        total_invested = sum(r["weekly_amount"] for r in results)
        weighted_score = sum(r["composite_score"] * r["weight_pct"] for r in results) / 100 if results else 0
        avg_vol = np.mean([r["volatility_30d"] for r in results]) if results else 0

        return {
            "portfolio_name": portfolio_name,
            "description": template["description"],
            "target_return": template["target_return"],
            "risk_level": template["risk_level"],
            "generated_at": datetime.now().isoformat(),
            "weekly_budget": weekly_budget,
            "total_weekly_investment": round(total_invested, 2),
            "num_holdings": len(results),
            "portfolio_composite_score": round(weighted_score, 1),
            "avg_volatility": round(avg_vol, 1),
            "holdings": results,
            "annual_projection": round(weekly_budget * 52, 2),
            "5yr_projection_low": round(weekly_budget * 52 * 5 * 1.06, 2),  # 6% conservative
            "5yr_projection_mid": round(weekly_budget * 52 * 5 * 1.10, 2),  # 10% moderate
            "5yr_projection_high": round(weekly_budget * 52 * 5 * 1.15, 2),  # 15% aggressive
        }


# ============================================================================
# JSON EXPORT
# ============================================================================

def export_recommendations_json(recommendations: Dict, filepath: str = None) -> str:
    """Export recommendations to structured JSON for dashboards/APIs"""

    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            elif isinstance(obj, (np.floating,)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)

    json_str = json.dumps(recommendations, cls=CustomEncoder, indent=2)

    if filepath:
        with open(filepath, 'w') as f:
            f.write(json_str)

    return json_str
