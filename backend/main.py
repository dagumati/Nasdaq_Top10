"""
Global Investment Research Platform — FastAPI Backend
======================================================
REST API serving the React frontend with data from:
  - Global market screener
  - Weekly DCA recommendations
  - Model portfolio builder
  - Nasdaq rotation strategy
  - Compound growth projections
"""

import sys
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Make parent directory (project root) importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.routers import screener, recommendations, portfolio, dca, nasdaq
except ModuleNotFoundError:
    from routers import screener, recommendations, portfolio, dca, nasdaq

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Global Investment Research API starting up...")
    yield
    logger.info("🛑 API shutting down...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Global Investment Research API",
    description=(
        "Multi-agent financial research platform for global equities, ETFs, "
        "and emerging markets. Powers the React frontend dashboard."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # CRA fallback
        "http://127.0.0.1:5173",
        os.getenv("FRONTEND_URL", ""),  # Production URL from env
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(screener.router,         prefix="/api/screener",         tags=["Screener"])
app.include_router(recommendations.router,  prefix="/api/recommendations",  tags=["Recommendations"])
app.include_router(portfolio.router,        prefix="/api/portfolio",         tags=["Portfolio"])
app.include_router(dca.router,              prefix="/api/dca",               tags=["DCA"])
app.include_router(nasdaq.router,           prefix="/api/nasdaq",            tags=["Nasdaq"])


# ── Health & Root ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "Global Investment Research API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": "2.0.0"}


# ── Global Error Handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
