"""
Screener Router — /api/screener
"""
import logging
import sys, os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from global_research_module import (
    GlobalResearchEngine,
    THEMATIC_ETF_UNIVERSE,
    GLOBAL_ETF_UNIVERSE,
    GLOBAL_GROWTH_STOCKS,
)

logger = logging.getLogger(__name__)
router = APIRouter()
_engine = GlobalResearchEngine()


@router.get("/universes")
async def list_universes():
    """Return available screening universes and their metadata"""
    return {
        "thematic": {
            "name": "Thematic ETFs",
            "themes": list(THEMATIC_ETF_UNIVERSE.keys()),
            "total_assets": sum(len(v["tickers"]) for v in THEMATIC_ETF_UNIVERSE.values()),
        },
        "global_etfs": {
            "name": "Global & Regional ETFs",
            "regions": list(GLOBAL_ETF_UNIVERSE.keys()),
            "total_assets": sum(len(v["tickers"]) for v in GLOBAL_ETF_UNIVERSE.values()),
        },
        "growth_stocks": {
            "name": "Global Growth Stocks",
            "categories": list(GLOBAL_GROWTH_STOCKS.keys()),
            "total_assets": sum(len(v) for v in GLOBAL_GROWTH_STOCKS.values()),
        },
    }


@router.get("/run")
async def run_screener(
    universe: str = Query(default="thematic", description="thematic | global_etfs | growth_stocks"),
    top_n: int = Query(default=15, ge=5, le=50),
    custom_tickers: Optional[str] = Query(default=None, description="Comma-separated tickers"),
):
    """
    Screen a universe of assets and return ranked results.
    Results are sorted by composite score (0–100).
    """
    logger.info(f"Running screener: universe={universe}, top_n={top_n}")

    universe_map = {
        "thematic": THEMATIC_ETF_UNIVERSE,
        "global_etfs": GLOBAL_ETF_UNIVERSE,
        "growth_stocks": GLOBAL_GROWTH_STOCKS,
    }

    if custom_tickers:
        tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
        universe_data = {"Custom": tickers}
    elif universe in universe_map:
        universe_data = universe_map[universe]
    else:
        raise HTTPException(status_code=400, detail=f"Unknown universe '{universe}'")

    try:
        results = _engine.screen_universe(universe_data, top_n=top_n)
        return {
            "universe": universe,
            "top_n": top_n,
            "total_returned": len(results),
            "generated_at": datetime.now().isoformat(),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Screener error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asset/{ticker}")
async def get_asset_detail(ticker: str):
    """Fetch detailed analysis for a single asset"""
    ticker = ticker.upper()
    logger.info(f"Asset detail: {ticker}")
    try:
        data = _engine.fetch_asset_data(ticker, period="1y")
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

        scores = _engine.calculate_composite_score(data)
        # Remove non-serialisable objects (DataFrames)
        serialisable = {k: v for k, v in data.items()
                        if k not in ("history", "returns")}

        return {"ticker": ticker, "data": serialisable, "scores": scores}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Asset detail error for {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
