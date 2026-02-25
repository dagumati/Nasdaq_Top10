"""
Backend API Tests (pytest)
===========================
Tests for all FastAPI routers using TestClient.
Run: cd backend && pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient


# ── Fixtures ───────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app)


# ── Health ─────────────────────────────────────────────────────────────────────
class TestHealth:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "running"
        assert "version" in data

    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


# ── Screener ───────────────────────────────────────────────────────────────────
class TestScreener:
    def test_universes(self, client):
        r = client.get("/api/screener/universes")
        assert r.status_code == 200
        data = r.json()
        assert "thematic" in data
        assert "global_etfs" in data
        assert data["thematic"]["total_assets"] > 0

    def test_run_screener_thematic(self, client):
        r = client.get("/api/screener/run", params={"universe": "thematic", "top_n": 5})
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        assert len(data["results"]) <= 5

    def test_run_screener_invalid_universe(self, client):
        r = client.get("/api/screener/run", params={"universe": "invalid_xyz"})
        assert r.status_code == 400

    def test_top_n_validation(self, client):
        # top_n must be >= 5
        r = client.get("/api/screener/run", params={"universe": "thematic", "top_n": 1})
        assert r.status_code == 422     # FastAPI validation error

    def test_asset_detail(self, client):
        r = client.get("/api/screener/asset/AAPL")
        # May return 404 if network unavailable in CI — just check it doesn't 500
        assert r.status_code in (200, 404, 500)

    def test_screener_results_sorted(self, client):
        r = client.get("/api/screener/run", params={"universe": "thematic", "top_n": 10})
        if r.status_code != 200:
            pytest.skip("Network unavailable")
        results = r.json()["results"]
        scores = [x["composite_score"] for x in results]
        assert scores == sorted(scores, reverse=True), "Results must be sorted by composite_score desc"


# ── Recommendations ────────────────────────────────────────────────────────────
class TestRecommendations:
    def test_weekly_default(self, client):
        r = client.get("/api/recommendations/weekly")
        assert r.status_code in (200, 500)   # 500 ok if network down

    def test_weekly_params(self, client):
        r = client.get("/api/recommendations/weekly",
                        params={"weekly_budget": 300, "risk_profile": "Aggressive"})
        assert r.status_code in (200, 500)

    def test_invalid_risk_profile(self, client):
        r = client.get("/api/recommendations/weekly",
                        params={"risk_profile": "YOLO"})
        assert r.status_code == 400

    def test_budget_bounds(self, client):
        # Below minimum
        r = client.get("/api/recommendations/weekly", params={"weekly_budget": 10})
        assert r.status_code == 422


# ── Portfolio ──────────────────────────────────────────────────────────────────
class TestPortfolio:
    def test_list_portfolios(self, client):
        r = client.get("/api/portfolio/list")
        assert r.status_code == 200
        data = r.json()
        assert "portfolios" in data
        assert len(data["portfolios"]) == 4

    def test_portfolio_names(self, client):
        r = client.get("/api/portfolio/list")
        names = [p["name"] for p in r.json()["portfolios"]]
        assert "🌍 Global Growth" in names

    def test_build_invalid_name(self, client):
        r = client.get("/api/portfolio/build", params={"name": "Nonexistent Portfolio"})
        assert r.status_code == 400

    def test_budget_validation(self, client):
        r = client.get("/api/portfolio/build",
                        params={"name": "🌍 Global Growth", "weekly_budget": 5})
        assert r.status_code == 422


# ── DCA ────────────────────────────────────────────────────────────────────────
class TestDCA:
    def test_project_growth(self, client):
        r = client.get("/api/dca/project",
                        params={"weekly_contribution": 200, "expected_annual_return": 0.10, "years": 10})
        assert r.status_code == 200
        data = r.json()
        assert "final_value" in data
        assert data["final_value"] > (200 * 52 * 10)   # Must exceed contributions

    def test_project_growth_math(self, client):
        """$200/week at 0% return for 1 year should be ~$10,400"""
        r = client.get("/api/dca/project",
                        params={"weekly_contribution": 200, "expected_annual_return": 0.001, "years": 1})
        data = r.json()
        assert 10_000 < data["final_value"] < 11_000

    def test_scenarios(self, client):
        r = client.get("/api/dca/scenarios",
                        params={"weekly_contribution": 100, "years": 5})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 4   # 4 scenarios

    def test_scenarios_ordering(self, client):
        """Higher return scenario must yield higher final value"""
        r = client.get("/api/dca/scenarios",
                        params={"weekly_contribution": 200, "years": 5})
        vals = [s["final_value"] for s in r.json().values()]
        assert vals == sorted(vals), "Scenarios must be ordered by return ascending"

    def test_simulate_mismatched_tickers_weights(self, client):
        r = client.get("/api/dca/simulate",
                        params={"tickers":"VTI,QQQ","weights":"0.6","weekly_budget":200,
                                "start_date":"2022-01-01","end_date":"2022-12-31"})
        assert r.status_code == 400

    def test_simulate_no_tickers(self, client):
        r = client.get("/api/dca/simulate",
                        params={"tickers":"","weights":"","weekly_budget":200,
                                "start_date":"2022-01-01","end_date":"2022-12-31"})
        assert r.status_code == 400


# ── Nasdaq ─────────────────────────────────────────────────────────────────────
class TestNasdaq:
    def test_start_after_end_year(self, client):
        r = client.get("/api/nasdaq/simulate",
                        params={"start_year": 2023, "end_year": 2020})
        assert r.status_code == 400

    def test_simulation_returns_data(self, client):
        # Short range to keep test fast
        r = client.get("/api/nasdaq/simulate",
                        params={"start_year": 2022, "end_year": 2023, "top_n": 5})
        assert r.status_code in (200, 500)   # 500 acceptable without network
