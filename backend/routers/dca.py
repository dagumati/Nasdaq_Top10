"""
DCA Router — /api/dca
"""
import logging
import sys, os
from fastapi import APIRouter, HTTPException, Query

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from weekly_dca_module import DCASimulator, GrowthProjector

logger = logging.getLogger(__name__)
router = APIRouter()
_simulator = DCASimulator()


@router.get("/project")
async def project_growth(
    weekly_contribution: float = Query(default=200.0, ge=10, le=5000),
    expected_annual_return: float = Query(default=0.10, ge=0.01, le=0.50),
    years: int = Query(default=10, ge=1, le=40),
    existing_balance: float = Query(default=0.0, ge=0),
):
    """Project compound portfolio growth from weekly DCA contributions"""
    logger.info(f"DCA projection: ${weekly_contribution}/wk @ {expected_annual_return*100:.0f}% for {years}yr")
    return GrowthProjector.project_growth(
        weekly_contribution, expected_annual_return, years, existing_balance
    )


@router.get("/scenarios")
async def dca_scenarios(
    weekly_contribution: float = Query(default=200.0, ge=10, le=5000),
    years: int = Query(default=10, ge=1, le=40),
    existing_balance: float = Query(default=0.0, ge=0),
):
    """Run DCA projections across 4 return scenarios (Conservative/Moderate/Aggressive/Optimistic)"""
    logger.info(f"DCA scenarios: ${weekly_contribution}/wk for {years}yr")
    return GrowthProjector.project_multiple_scenarios(
        weekly_contribution, years, existing_balance
    )


@router.get("/simulate")
async def simulate_dca(
    tickers: str = Query(description="Comma-separated tickers e.g. VTI,QQQ,VWO"),
    weights: str = Query(description="Comma-separated weights (same order) e.g. 0.6,0.3,0.1"),
    weekly_budget: float = Query(default=200.0, ge=50, le=2000),
    start_date: str = Query(default="2020-01-01", description="YYYY-MM-DD"),
    end_date: str = Query(default="2024-12-31", description="YYYY-MM-DD"),
):
    """
    Simulate DCA investing historically with real weekly price data.
    Returns week-by-week portfolio history and final holdings breakdown.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    weight_list = [float(w.strip()) for w in weights.split(",") if w.strip()]

    if len(ticker_list) != len(weight_list):
        raise HTTPException(status_code=400, detail="Number of tickers must match number of weights")
    if len(ticker_list) == 0:
        raise HTTPException(status_code=400, detail="At least one ticker required")

    portfolio = dict(zip(ticker_list, weight_list))

    logger.info(f"DCA simulate: {portfolio}, ${weekly_budget}/wk, {start_date}→{end_date}")
    try:
        result = _simulator.simulate_dca(portfolio, weekly_budget, start_date, end_date)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DCA simulate error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
