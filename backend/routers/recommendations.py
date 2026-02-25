"""
Recommendations Router — /api/recommendations
"""
import logging
import sys, os
from fastapi import APIRouter, HTTPException, Query
from typing import Literal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from global_research_module import GlobalResearchEngine, export_recommendations_json

logger = logging.getLogger(__name__)
router = APIRouter()
_engine = GlobalResearchEngine()


@router.get("/weekly")
async def get_weekly_recommendations(
    weekly_budget: float = Query(default=200.0, ge=50, le=2000,
                                  description="Weekly investment budget in USD"),
    risk_profile: str = Query(default="Moderate",
                               description="Conservative | Moderate | Aggressive"),
):
    """
    Generate weekly investment recommendations personalised to budget and risk profile.
    Returns per-position allocations with fractional share counts and reasoning.
    """
    if risk_profile not in ("Conservative", "Moderate", "Aggressive"):
        raise HTTPException(status_code=400, detail="risk_profile must be Conservative | Moderate | Aggressive")

    logger.info(f"Generating weekly recommendations: budget=${weekly_budget}, risk={risk_profile}")
    try:
        result = _engine.generate_weekly_recommendations(
            weekly_budget=weekly_budget,
            risk_profile=risk_profile,
        )
        return result
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weekly/json")
async def get_weekly_recommendations_json(
    weekly_budget: float = Query(default=200.0, ge=50, le=2000),
    risk_profile: str = Query(default="Moderate"),
):
    """Same as /weekly but returns raw JSON string for direct pipeline ingestion"""
    try:
        result = _engine.generate_weekly_recommendations(
            weekly_budget=weekly_budget,
            risk_profile=risk_profile,
        )
        return {"json": export_recommendations_json(result)}
    except Exception as e:
        logger.error(f"JSON recommendation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
