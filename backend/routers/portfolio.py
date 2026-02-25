"""
Portfolio Router — /api/portfolio
"""
import logging
import sys, os
from fastapi import APIRouter, HTTPException, Query

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from global_research_module import GlobalResearchEngine, ModelPortfolioBuilder

logger = logging.getLogger(__name__)
router = APIRouter()
_engine = GlobalResearchEngine()
_builder = ModelPortfolioBuilder(_engine)


@router.get("/list")
async def list_portfolios():
    """Return all available model portfolio names and templates (without live data)"""
    portfolios = []
    for name, template in ModelPortfolioBuilder.PORTFOLIO_TEMPLATES.items():
        portfolios.append({
            "name": name,
            "description": template["description"],
            "target_return": template["target_return"],
            "risk_level": template["risk_level"],
            "num_holdings": len(template["holdings"]),
            "holdings_preview": list(template["holdings"].keys()),
        })
    return {"portfolios": portfolios}


@router.get("/build")
async def build_portfolio(
    name: str = Query(description="Portfolio name (use /list to see options)"),
    weekly_budget: float = Query(default=200.0, ge=50, le=2000),
):
    """
    Build a named model portfolio with live market data.
    Returns holdings scored with current prices, returns, and weekly allocation amounts.
    """
    logger.info(f"Building portfolio '{name}' with ${weekly_budget}/week")

    # Validate
    available = _builder.get_portfolio_names()
    if name not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Portfolio '{name}' not found. Available: {available}"
        )

    try:
        result = _builder.build_portfolio_with_live_data(name, weekly_budget=weekly_budget)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio build error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
