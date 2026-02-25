"""
Weekly Dollar-Cost Averaging (DCA) Module
==========================================
Simulates and tracks weekly fractional share investments for everyday investors.
Supports $100-$400 weekly contributions across diversified portfolios.

Features:
- DCA simulation with historical data
- Fractional share calculation
- Cost-basis tracking
- Performance attribution
- Compound growth projections
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import warnings
warnings.filterwarnings('ignore')


class DCASimulator:
    """
    Dollar-Cost Averaging simulator that models recurring weekly investments.
    Demonstrates the power of consistent investing over time.
    """

    def __init__(self):
        self._price_cache = {}

    def _fetch_prices(self, ticker: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """Fetch historical weekly prices for a ticker"""
        cache_key = f"{ticker}_{start}_{end}"
        if cache_key in self._price_cache:
            return self._price_cache[cache_key]

        try:
            data = yf.download(ticker, start=start, end=end, interval="1wk", progress=False)
            if data.empty:
                return None
            # Handle MultiIndex columns from yf.download
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            self._price_cache[cache_key] = data
            return data
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None

    def simulate_dca(self, portfolio: Dict[str, float], weekly_budget: float,
                     start_date: str, end_date: str,
                     progress_callback=None) -> Dict:
        """
        Simulate DCA investing over a period.

        Args:
            portfolio: Dict of {ticker: weight} e.g., {"VTI": 0.40, "QQQ": 0.30, "VWO": 0.30}
            weekly_budget: Weekly investment amount
            start_date: "YYYY-MM-DD"
            end_date: "YYYY-MM-DD"

        Returns:
            Comprehensive simulation results
        """
        # Normalize weights
        total_weight = sum(portfolio.values())
        portfolio = {k: v / total_weight for k, v in portfolio.items()}

        # Fetch all price data
        price_data = {}
        total_tickers = len(portfolio)
        for idx, (ticker, weight) in enumerate(portfolio.items()):
            if progress_callback:
                progress_callback(idx / total_tickers, f"Loading {ticker} price data...")

            prices = self._fetch_prices(ticker, start_date, end_date)
            if prices is not None:
                price_data[ticker] = prices

        if not price_data:
            return {"error": "No price data available for any ticker"}

        # Find common date range
        all_dates = None
        for ticker, prices in price_data.items():
            dates = set(prices.index)
            if all_dates is None:
                all_dates = dates
            else:
                all_dates = all_dates.intersection(dates)

        common_dates = sorted(list(all_dates))

        if len(common_dates) < 4:
            return {"error": "Insufficient overlapping data"}

        # ---- Run DCA Simulation ----
        holdings = {ticker: {"shares": 0.0, "cost_basis": 0.0} for ticker in price_data}
        weekly_records = []
        total_invested = 0.0

        for week_idx, date in enumerate(common_dates):
            week_investment = weekly_budget
            total_invested += week_investment
            week_record = {
                "date": date.strftime("%Y-%m-%d"),
                "week_number": week_idx + 1,
                "weekly_investment": week_investment,
                "total_invested": round(total_invested, 2),
                "purchases": {},
                "portfolio_value": 0.0,
            }

            for ticker, weight in portfolio.items():
                if ticker not in price_data:
                    continue

                prices = price_data[ticker]
                if date not in prices.index:
                    continue

                price = float(prices.loc[date, 'Close'])
                if price <= 0:
                    continue

                amount = week_investment * weight
                shares_bought = amount / price

                holdings[ticker]["shares"] += shares_bought
                holdings[ticker]["cost_basis"] += amount

                week_record["purchases"][ticker] = {
                    "price": round(price, 2),
                    "shares_bought": round(shares_bought, 6),
                    "amount_invested": round(amount, 2),
                    "total_shares": round(holdings[ticker]["shares"], 6),
                }

            # Calculate portfolio value at this date
            portfolio_value = 0.0
            for ticker in price_data:
                if date in price_data[ticker].index:
                    current_price = float(price_data[ticker].loc[date, 'Close'])
                    portfolio_value += holdings[ticker]["shares"] * current_price

            week_record["portfolio_value"] = round(portfolio_value, 2)
            week_record["total_gain_loss"] = round(portfolio_value - total_invested, 2)
            week_record["total_return_pct"] = round(
                ((portfolio_value / total_invested) - 1) * 100, 2
            ) if total_invested > 0 else 0

            weekly_records.append(week_record)

            if progress_callback:
                pct = (week_idx + 1) / len(common_dates)
                progress_callback(0.5 + pct * 0.5, f"Simulating week {week_idx + 1}/{len(common_dates)}")

        # ---- Final Summary ----
        final = weekly_records[-1] if weekly_records else {}
        final_value = final.get("portfolio_value", 0)

        # Individual holding performance
        holding_details = []
        for ticker in price_data:
            if holdings[ticker]["shares"] <= 0:
                continue

            last_date = common_dates[-1]
            if last_date in price_data[ticker].index:
                current_price = float(price_data[ticker].loc[last_date, 'Close'])
            else:
                continue

            market_value = holdings[ticker]["shares"] * current_price
            cost = holdings[ticker]["cost_basis"]
            gain = market_value - cost
            avg_cost_per_share = cost / holdings[ticker]["shares"] if holdings[ticker]["shares"] > 0 else 0

            holding_details.append({
                "ticker": ticker,
                "total_shares": round(holdings[ticker]["shares"], 4),
                "avg_cost_per_share": round(avg_cost_per_share, 2),
                "current_price": round(current_price, 2),
                "cost_basis": round(cost, 2),
                "market_value": round(market_value, 2),
                "unrealized_gain": round(gain, 2),
                "return_pct": round((gain / cost) * 100, 2) if cost > 0 else 0,
                "weight_actual": round((market_value / final_value) * 100, 1) if final_value > 0 else 0,
                "weight_target": round(portfolio.get(ticker, 0) * 100, 1),
            })

        holding_details.sort(key=lambda x: x["market_value"], reverse=True)

        # Calculate CAGR
        weeks = len(common_dates)
        years = weeks / 52
        cagr = ((final_value / total_invested) ** (1 / years) - 1) * 100 if years > 0 and total_invested > 0 else 0

        if progress_callback:
            progress_callback(1.0, "Simulation complete!")

        return {
            "simulation_period": {
                "start": common_dates[0].strftime("%Y-%m-%d") if common_dates else "",
                "end": common_dates[-1].strftime("%Y-%m-%d") if common_dates else "",
                "total_weeks": weeks,
                "total_years": round(years, 1),
            },
            "summary": {
                "weekly_contribution": weekly_budget,
                "total_invested": round(total_invested, 2),
                "final_portfolio_value": round(final_value, 2),
                "total_gain_loss": round(final_value - total_invested, 2),
                "total_return_pct": round(((final_value / total_invested) - 1) * 100, 2) if total_invested > 0 else 0,
                "cagr_pct": round(cagr, 2),
                "num_positions": len(holding_details),
            },
            "holdings": holding_details,
            "weekly_history": weekly_records,
        }


class GrowthProjector:
    """
    Project future portfolio growth based on DCA contributions and expected returns.
    """

    @staticmethod
    def project_growth(weekly_contribution: float,
                       expected_annual_return: float = 0.10,
                       years: int = 10,
                       existing_balance: float = 0.0) -> Dict:
        """
        Project portfolio growth over time.

        Args:
            weekly_contribution: Weekly investment amount
            expected_annual_return: Expected annual return (decimal, e.g., 0.10 for 10%)
            years: Number of years to project
            existing_balance: Starting portfolio balance

        Returns:
            Year-by-year projection
        """
        weekly_return = (1 + expected_annual_return) ** (1/52) - 1
        annual_contribution = weekly_contribution * 52

        projections = []
        balance = existing_balance

        for year in range(1, years + 1):
            # Week-by-week compounding
            for week in range(52):
                balance = balance * (1 + weekly_return) + weekly_contribution

            total_contributions = existing_balance + annual_contribution * year
            investment_growth = balance - total_contributions

            projections.append({
                "year": year,
                "total_contributions": round(total_contributions, 2),
                "portfolio_value": round(balance, 2),
                "investment_growth": round(investment_growth, 2),
                "growth_pct": round((investment_growth / total_contributions) * 100, 1) if total_contributions > 0 else 0,
            })

        return {
            "weekly_contribution": weekly_contribution,
            "annual_contribution": annual_contribution,
            "expected_annual_return": f"{expected_annual_return * 100}%",
            "projection_years": years,
            "starting_balance": existing_balance,
            "projections": projections,
            "final_value": round(balance, 2),
            "total_contributions": round(existing_balance + annual_contribution * years, 2),
            "total_growth": round(balance - (existing_balance + annual_contribution * years), 2),
        }

    @staticmethod
    def project_multiple_scenarios(weekly_contribution: float,
                                   years: int = 10,
                                   existing_balance: float = 0.0) -> Dict:
        """Run projections across multiple return scenarios"""
        scenarios = {
            "Conservative (6%)": 0.06,
            "Moderate (10%)": 0.10,
            "Aggressive (14%)": 0.14,
            "Optimistic (18%)": 0.18,
        }

        results = {}
        for name, rate in scenarios.items():
            proj = GrowthProjector.project_growth(
                weekly_contribution, rate, years, existing_balance
            )
            results[name] = {
                "final_value": proj["final_value"],
                "total_contributions": proj["total_contributions"],
                "total_growth": proj["total_growth"],
                "projections": proj["projections"],
            }

        return results
