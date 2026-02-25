"""
Pydantic Schemas — Request & Response Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────
class RiskProfile(str, Enum):
    conservative = "Conservative"
    moderate = "Moderate"
    aggressive = "Aggressive"


class UniverseType(str, Enum):
    thematic = "Thematic ETFs"
    global_etfs = "Global & Regional ETFs"
    growth_stocks = "Global Growth Stocks"


class PortfolioName(str, Enum):
    global_growth = "🌍 Global Growth"
    conservative = "🛡️ Conservative Income"
    aggressive = "🚀 Aggressive Innovation"
    esg = "🌱 ESG & Impact"


# ── Screener ──────────────────────────────────────────────────────────────────
class ScreenerRequest(BaseModel):
    universe: UniverseType = UniverseType.thematic
    top_n: int = Field(default=15, ge=5, le=50)
    custom_tickers: Optional[List[str]] = None


class AssetScore(BaseModel):
    ticker: str
    name: str
    category: str
    sector: Optional[str]
    country: Optional[str]
    current_price: float
    market_cap: Optional[float]
    return_1m: float
    return_3m: float
    return_6m: float
    return_1y: float
    volatility_30d: float
    sharpe_ratio: float
    max_drawdown: float
    momentum_score: float
    trend_strength: str
    volume_trend: str
    composite_score: float
    rating: str
    confidence: str
    fundamental_score: float
    momentum_sub_score: float
    risk_adjusted_score: float
    macro_alignment_score: float


class ScreenerResponse(BaseModel):
    universe: str
    top_n: int
    results: List[AssetScore]
    generated_at: str


# ── Recommendations ───────────────────────────────────────────────────────────
class RecommendationRequest(BaseModel):
    weekly_budget: float = Field(default=200.0, ge=50, le=2000)
    risk_profile: RiskProfile = RiskProfile.moderate


class Recommendation(BaseModel):
    bucket: str
    ticker: str
    name: str
    allocation_pct: float
    weekly_amount: float
    current_price: float
    fractional_shares: float
    composite_score: float
    rating: str
    return_3m: float
    volatility: float
    trend: str
    reason: str


class PortfolioMetrics(BaseModel):
    total_weekly_investment: float
    weighted_composite_score: float
    weighted_volatility: float
    num_positions: int
    num_buckets: int
    diversification_score: float


class RecommendationResponse(BaseModel):
    generated_at: str
    weekly_budget: float
    risk_profile: str
    total_positions: int
    allocation_summary: Dict[str, float]
    recommendations: List[Recommendation]
    portfolio_metrics: PortfolioMetrics
    disclaimer: str


# ── Portfolio ─────────────────────────────────────────────────────────────────
class PortfolioRequest(BaseModel):
    portfolio_name: PortfolioName = PortfolioName.global_growth
    weekly_budget: float = Field(default=200.0, ge=50, le=2000)


class HoldingDetail(BaseModel):
    ticker: str
    name: str
    role: str
    weight_pct: float
    weekly_amount: float
    fractional_shares: float
    current_price: float
    return_3m: float
    return_6m: float
    volatility_30d: float
    sharpe_ratio: float
    max_drawdown: float
    composite_score: float
    rating: str
    trend_strength: str


class PortfolioResponse(BaseModel):
    portfolio_name: str
    description: str
    target_return: str
    risk_level: str
    generated_at: str
    weekly_budget: float
    total_weekly_investment: float
    num_holdings: int
    portfolio_composite_score: float
    avg_volatility: float
    holdings: List[HoldingDetail]
    annual_projection: float
    five_yr_projection_low: float
    five_yr_projection_mid: float
    five_yr_projection_high: float


class PortfolioListResponse(BaseModel):
    portfolios: List[Dict[str, Any]]


# ── DCA ───────────────────────────────────────────────────────────────────────
class DCASimulateRequest(BaseModel):
    portfolio: Dict[str, float]          # e.g. {"VTI": 0.6, "QQQ": 0.4}
    weekly_budget: float = Field(default=200.0, ge=50, le=2000)
    start_date: str                      # "YYYY-MM-DD"
    end_date: str                        # "YYYY-MM-DD"


class DCAProjectRequest(BaseModel):
    weekly_contribution: float = Field(default=200.0, ge=10, le=5000)
    expected_annual_return: float = Field(default=0.10, ge=0.01, le=0.50)
    years: int = Field(default=10, ge=1, le=40)
    existing_balance: float = Field(default=0.0, ge=0)


class DCAScenarioRequest(BaseModel):
    weekly_contribution: float = Field(default=200.0, ge=10, le=5000)
    years: int = Field(default=10, ge=1, le=40)
    existing_balance: float = Field(default=0.0, ge=0)


# ── Nasdaq ────────────────────────────────────────────────────────────────────
class NasdaqSimulateRequest(BaseModel):
    initial_capital: float = Field(default=20000.0, ge=1000)
    start_year: int = Field(default=2018, ge=2000, le=2024)
    end_year: int = Field(default=2024, ge=2001, le=2025)
    top_n: int = Field(default=10, ge=5, le=20)
    strategy: str = Field(default="Full Rebalancing")
