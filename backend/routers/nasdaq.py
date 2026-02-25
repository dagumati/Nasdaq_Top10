"""
Nasdaq Router — /api/nasdaq
Exposes the existing Nasdaq rotation simulation as a REST endpoint.
"""
import logging
import sys, os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/simulate")
async def simulate_nasdaq_rotation(
    initial_capital: float = Query(default=20000.0, ge=1000),
    start_year: int = Query(default=2018, ge=2000, le=2024),
    end_year: int = Query(default=2024, ge=2001, le=2025),
    top_n: int = Query(default=10, ge=5, le=20),
    strategy: str = Query(default="Full Rebalancing"),
):
    """
    Run the Nasdaq 100 quarterly top-N rotation simulation.
    Heavy operation — expect 30-60 seconds for multi-year runs.
    """
    if start_year >= end_year:
        raise HTTPException(status_code=400, detail="start_year must be before end_year")

    logger.info(f"Nasdaq rotation: {start_year}→{end_year}, top_n={top_n}, strategy={strategy}")

    try:
        from nasdaq_rotation_module import (
            OptimizedYahooDataFetcher,
            OptimizedPortfolioSimulator,
        )

        start_dt = datetime(start_year, 1, 1)
        end_dt = datetime(end_year, 12, 31)

        fetcher = OptimizedYahooDataFetcher()
        simulator = OptimizedPortfolioSimulator(initial_capital, fetcher)
        results = simulator.simulate(start_dt, end_dt, top_n=top_n, strategy=strategy)

        if not results:
            raise HTTPException(status_code=500, detail="Simulation returned no results")

        # Serialise — strip any non-JSON-safe objects
        def safe(obj):
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            return str(obj)

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Nasdaq simulation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/universe")
async def get_nasdaq_universe():
    """Return the list of Nasdaq tickers used in the rotation strategy"""
    try:
        from nasdaq_rotation_module import OptimizedYahooDataFetcher
        fetcher = OptimizedYahooDataFetcher()
        return {"tickers": fetcher.NASDAQ_100_TICKERS}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
