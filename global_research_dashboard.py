"""
Global Investment Research Dashboard
=====================================
Streamlit dashboard tabs for the Global Research Engine, Weekly DCA Simulator,
and Model Portfolio Builder. Designed for everyday investors.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from global_research_module import (
    GlobalResearchEngine,
    ModelPortfolioBuilder,
    THEMATIC_ETF_UNIVERSE,
    GLOBAL_ETF_UNIVERSE,
    GLOBAL_GROWTH_STOCKS,
    export_recommendations_json,
)
from weekly_dca_module import DCASimulator, GrowthProjector


# ============================================================================
# CUSTOM STYLING
# ============================================================================

def inject_custom_css():
    """Inject premium CSS styling for the dashboard"""
    st.markdown("""
    <style>
    /* ---- Global Premium Theme ---- */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(30,30,60,0.9) 0%, rgba(40,40,80,0.7) 100%);
        border: 1px solid rgba(100,100,255,0.15);
        border-radius: 16px;
        padding: 20px;
        margin: 8px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(80,80,255,0.2);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .metric-label {
        font-size: 0.85rem;
        color: rgba(200,200,230,0.7);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }

    .metric-delta-positive {
        color: #00d4aa;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .metric-delta-negative {
        color: #ff6b6b;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .section-header {
        background: linear-gradient(90deg, rgba(102,126,234,0.15), rgba(118,75,162,0.05));
        border-left: 4px solid #667eea;
        padding: 12px 20px;
        border-radius: 0 12px 12px 0;
        margin: 24px 0 16px 0;
        font-size: 1.2rem;
        font-weight: 600;
        color: #e0e0ff;
    }

    .recommendation-card {
        background: rgba(25,25,50,0.8);
        border: 1px solid rgba(100,100,255,0.1);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    .recommendation-card:hover {
        border-color: rgba(100,100,255,0.3);
        box-shadow: 0 4px 20px rgba(80,80,255,0.15);
    }

    .badge-buy {
        background: linear-gradient(135deg, #00d4aa, #00b894);
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-hold {
        background: linear-gradient(135deg, #ffd93d, #f0c040);
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-sell {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: #fff;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }

    .portfolio-template-card {
        background: linear-gradient(135deg, rgba(30,30,60,0.95), rgba(40,40,80,0.8));
        border: 1px solid rgba(100,100,255,0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
    }

    .projection-highlight {
        background: linear-gradient(135deg, rgba(0,212,170,0.1), rgba(0,184,148,0.05));
        border: 1px solid rgba(0,212,170,0.3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    /* Clean up Streamlit defaults */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def render_metric_card(label: str, value: str, delta: str = "", delta_positive: bool = True):
    """Render a premium metric card"""
    delta_class = "metric-delta-positive" if delta_positive else "metric-delta-negative"
    delta_html = f'<p class="{delta_class}">{delta}</p>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">{label}</p>
        <p class="metric-value">{value}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(text: str):
    """Render a styled section header"""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def get_rating_badge(rating: str) -> str:
    """Return HTML badge for rating"""
    if "Buy" in rating:
        return f'<span class="badge-buy">{rating}</span>'
    elif "Hold" in rating:
        return f'<span class="badge-hold">{rating}</span>'
    else:
        return f'<span class="badge-sell">{rating}</span>'


def format_currency(amount: float) -> str:
    """Format number as currency"""
    if abs(amount) >= 1e9:
        return f"${amount/1e9:.1f}B"
    elif abs(amount) >= 1e6:
        return f"${amount/1e6:.1f}M"
    elif abs(amount) >= 1e3:
        return f"${amount/1e3:.1f}K"
    else:
        return f"${amount:,.2f}"


# ============================================================================
# TAB 1: GLOBAL MARKET SCREENER
# ============================================================================

def global_screener_tab():
    """Global Market Screener & Research Tab"""
    inject_custom_css()

    st.markdown("## 🌍 Global Market Screener")
    st.markdown("""
    <p style="color: rgba(200,200,230,0.7); font-size: 1.05rem; margin-bottom: 24px;">
    Screen global equities, ETFs, and emerging markets. Identify opportunities across
    thematic sectors, frontier markets, and high-growth regions — scored by fundamentals,
    momentum, risk, and macro alignment.
    </p>
    """, unsafe_allow_html=True)

    # ---- Sidebar Configuration ----
    with st.sidebar:
        st.markdown("### 🔬 Screener Settings")

        universe_choice = st.selectbox(
            "Select Universe",
            ["Thematic ETFs", "Global & Regional ETFs", "Global Growth Stocks", "Custom Tickers"],
            help="Choose which universe to screen"
        )

        top_n = st.slider("Show Top N Results", 5, 30, 15)

    # ---- Main Content ----
    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card(
            "Universes Available",
            f"{len(THEMATIC_ETF_UNIVERSE) + len(GLOBAL_ETF_UNIVERSE)}",
            "Thematic + Global"
        )
    with col2:
        total_etfs = sum(len(v["tickers"]) for v in THEMATIC_ETF_UNIVERSE.values()) + \
                     sum(len(v["tickers"]) for v in GLOBAL_ETF_UNIVERSE.values())
        render_metric_card("Total Assets Tracked", str(total_etfs), "ETFs & Stocks")
    with col3:
        total_stocks = sum(len(v) for v in GLOBAL_GROWTH_STOCKS.values())
        render_metric_card("Growth Stocks", str(total_stocks), "Global Leaders")

    # ---- Custom Tickers Input ----
    custom_tickers = []
    if universe_choice == "Custom Tickers":
        custom_input = st.text_area(
            "Enter tickers (comma-separated)",
            "VTI, QQQ, VWO, INDA, SOXX, ICLN, GLD",
            help="Enter stock or ETF tickers separated by commas"
        )
        custom_tickers = [t.strip().upper() for t in custom_input.split(",") if t.strip()]

    # ---- Universe Preview ----
    if universe_choice == "Thematic ETFs":
        render_section_header("📡 Thematic ETF Universe")
        cols = st.columns(3)
        for idx, (theme, info) in enumerate(THEMATIC_ETF_UNIVERSE.items()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="recommendation-card">
                    <h4 style="color: #667eea; margin: 0 0 4px 0;">{theme}</h4>
                    <p style="color: rgba(200,200,230,0.6); font-size: 0.85rem; margin: 0 0 6px 0;">
                        {info['description']}
                    </p>
                    <p style="color: rgba(200,200,230,0.4); font-size: 0.75rem; margin: 0;">
                        🏷️ {info['macro_theme']} &nbsp;|&nbsp; 📊 {', '.join(info['tickers'])}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    elif universe_choice == "Global & Regional ETFs":
        render_section_header("🌐 Global & Regional ETF Universe")
        cols = st.columns(3)
        for idx, (region, info) in enumerate(GLOBAL_ETF_UNIVERSE.items()):
            with cols[idx % 3]:
                risk_color = {
                    "Low": "#00d4aa",
                    "Medium": "#ffd93d",
                    "High": "#ff6b6b",
                    "Very High": "#ff4444",
                    "Low-Medium": "#80e0c0",
                    "Medium-High": "#ffaa33",
                }.get(info["risk_level"], "#aaa")

                st.markdown(f"""
                <div class="recommendation-card">
                    <h4 style="color: #667eea; margin: 0 0 4px 0;">{region}</h4>
                    <p style="color: rgba(200,200,230,0.6); font-size: 0.85rem; margin: 0 0 6px 0;">
                        🌍 {info['region']}
                    </p>
                    <p style="color: rgba(200,200,230,0.4); font-size: 0.75rem; margin: 0;">
                        <span style="color: {risk_color};">⚡ {info['risk_level']} Risk</span>
                        &nbsp;|&nbsp; 📊 {', '.join(info['tickers'])}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ---- Run Screener ----
    if st.button("🔍 Run Screener", type="primary", use_container_width=True):
        engine = GlobalResearchEngine()

        # Build universe dict
        if universe_choice == "Thematic ETFs":
            universe = THEMATIC_ETF_UNIVERSE
        elif universe_choice == "Global & Regional ETFs":
            universe = GLOBAL_ETF_UNIVERSE
        elif universe_choice == "Global Growth Stocks":
            universe = GLOBAL_GROWTH_STOCKS
        else:
            universe = {"Custom": custom_tickers}

        progress_bar = st.progress(0, text="Starting analysis...")

        def update_progress(pct, text):
            progress_bar.progress(min(pct, 1.0), text=text)

        with st.spinner("Analyzing assets..."):
            results = engine.screen_universe(universe, top_n=top_n,
                                             progress_callback=update_progress)

        progress_bar.empty()

        if not results:
            st.warning("No results returned. Please try a different universe.")
            return

        # ---- Display Results ----
        render_section_header(f"🏆 Top {len(results)} Ranked Assets")

        # Results DataFrame
        df = pd.DataFrame(results)
        display_cols = [
            "ticker", "name", "category", "current_price",
            "composite_score", "rating", "return_1m", "return_3m",
            "return_6m", "volatility_30d", "sharpe_ratio",
            "momentum_score", "trend_strength"
        ]
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[available_cols].style.background_gradient(
                subset=["composite_score"], cmap="YlGn"
            ).format({
                "current_price": "${:.2f}",
                "return_1m": "{:.1f}%",
                "return_3m": "{:.1f}%",
                "return_6m": "{:.1f}%",
                "volatility_30d": "{:.1f}%",
                "sharpe_ratio": "{:.2f}",
            }),
            use_container_width=True,
            height=500
        )

        # ---- Score Distribution Chart ----
        render_section_header("📊 Score Breakdown")

        fig = go.Figure()
        for _, row in df.iterrows():
            fig.add_trace(go.Bar(
                name=row["ticker"],
                x=["Fundamental", "Momentum", "Risk-Adjusted", "Macro"],
                y=[row["fundamental_score"], row["momentum_sub_score"],
                   row["risk_adjusted_score"], row["macro_alignment_score"]],
                text=[f"{v:.0f}" for v in [row["fundamental_score"], row["momentum_sub_score"],
                                           row["risk_adjusted_score"], row["macro_alignment_score"]]],
                textposition='auto',
            ))

        fig.update_layout(
            barmode='group',
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            title="Score Components by Asset",
            font=dict(color='rgba(200,200,230,0.8)'),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---- Bubble Chart ----
        render_section_header("🫧 Risk-Return Landscape")

        fig2 = px.scatter(
            df, x="volatility_30d", y="return_3m",
            size="composite_score", color="category",
            hover_name="ticker", hover_data=["name", "rating", "sharpe_ratio"],
            labels={
                "volatility_30d": "30-Day Volatility (%)",
                "return_3m": "3-Month Return (%)",
                "composite_score": "Score"
            },
            title="Risk vs Return (bubble size = composite score)",
        )
        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500,
            font=dict(color='rgba(200,200,230,0.8)'),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ---- JSON Export ----
        with st.expander("📤 Export as JSON (for API/Dashboard Integration)"):
            json_out = export_recommendations_json({"screener_results": results})
            st.code(json_out, language="json")
            st.download_button(
                "⬇️ Download JSON",
                json_out,
                file_name=f"global_screener_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )


# ============================================================================
# TAB 2: WEEKLY INVESTMENT RECOMMENDATIONS
# ============================================================================

def weekly_recommendations_tab():
    """Weekly Investment Recommendations Tab"""
    inject_custom_css()

    st.markdown("## 💰 Weekly Investment Recommendations")
    st.markdown("""
    <p style="color: rgba(200,200,230,0.7); font-size: 1.05rem; margin-bottom: 24px;">
    Get personalized weekly investment recommendations based on your budget and risk profile.
    Uses fractional shares so you can invest as little as $5 per position per week.
    </p>
    """, unsafe_allow_html=True)

    # ---- Configuration ----
    with st.sidebar:
        st.markdown("### 💵 Weekly Budget")

        weekly_budget = st.slider(
            "Weekly Contribution ($)",
            min_value=50, max_value=500, value=200, step=25,
            help="How much you invest per week via recurring purchases"
        )

        risk_profile = st.selectbox(
            "Risk Profile",
            ["Conservative", "Moderate", "Aggressive"],
            index=1,
            help="Your risk tolerance"
        )

    # ---- Summary Cards ----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Weekly Budget", f"${weekly_budget}", "Recurring investment")
    with col2:
        render_metric_card("Monthly", f"${weekly_budget * 4:,.0f}", f"${weekly_budget * 52:,.0f}/year")
    with col3:
        render_metric_card("Risk Profile", risk_profile, "Selected profile")
    with col4:
        projected_5yr = weekly_budget * 52 * 5 * 1.10
        render_metric_card("5-Year Target", format_currency(projected_5yr), "@ 10% CAGR")

    # ---- Generate Recommendations ----
    if st.button("🚀 Generate This Week's Recommendations", type="primary", use_container_width=True):
        engine = GlobalResearchEngine()
        progress = st.progress(0, text="Starting research...")

        def update_progress(pct, text):
            progress.progress(min(pct, 1.0), text=text)

        with st.spinner("Analyzing markets..."):
            recs = engine.generate_weekly_recommendations(
                weekly_budget=weekly_budget,
                risk_profile=risk_profile,
                progress_callback=update_progress
            )

        progress.empty()

        recommendations = recs.get("recommendations", [])
        if not recommendations:
            st.warning("Could not generate recommendations. Please try again.")
            return

        # ---- Portfolio Metrics ----
        metrics = recs.get("portfolio_metrics", {})
        render_section_header("📊 Portfolio Overview")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Positions", str(metrics.get("num_positions", 0)), "Diversified holdings")
        with col2:
            render_metric_card("Buckets", str(metrics.get("num_buckets", 0)), "Asset categories")
        with col3:
            render_metric_card("Avg Score",
                             f"{metrics.get('weighted_composite_score', 0):.0f}/100",
                             "Weighted composite")
        with col4:
            render_metric_card("Diversification",
                             f"{metrics.get('diversification_score', 0)}/100",
                             "Sector spread")

        # ---- Allocation Pie Chart ----
        render_section_header("🥧 Weekly Allocation Breakdown")

        # Group by bucket
        bucket_totals = {}
        for r in recommendations:
            bucket = r["bucket"]
            bucket_totals[bucket] = bucket_totals.get(bucket, 0) + r["weekly_amount"]

        fig = go.Figure(data=[go.Pie(
            labels=list(bucket_totals.keys()),
            values=list(bucket_totals.values()),
            hole=0.45,
            textinfo='label+percent',
            textfont=dict(size=12),
            marker=dict(colors=px.colors.qualitative.Set3),
        )])
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            title=f"Weekly ${weekly_budget} Allocation",
            font=dict(color='rgba(200,200,230,0.8)'),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---- Detailed Recommendations ----
        render_section_header("📋 Individual Recommendations")

        for rec in recommendations:
            badge = get_rating_badge(rec["rating"])
            trend_emoji = "📈" if "Up" in str(rec["trend"]) else "📉" if "Down" in str(rec["trend"]) else "➡️"

            st.markdown(f"""
            <div class="recommendation-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: #e0e0ff; margin: 0;">
                            {rec['ticker']} — {rec['name']}
                        </h4>
                        <p style="color: rgba(200,200,230,0.5); margin: 2px 0; font-size: 0.85rem;">
                            🪣 {rec['bucket']} &nbsp;|&nbsp;
                            {trend_emoji} {rec['trend']} &nbsp;|&nbsp;
                            Score: {rec['composite_score']}/100
                        </p>
                    </div>
                    <div style="text-align: right;">
                        {badge}
                        <p style="color: #667eea; font-size: 1.3rem; font-weight: 700; margin: 4px 0 0 0;">
                            ${rec['weekly_amount']:.2f}/week
                        </p>
                    </div>
                </div>
                <p style="color: rgba(200,200,230,0.6); font-size: 0.85rem; margin: 8px 0 0 0;">
                    💵 Price: ${rec['current_price']:.2f} &nbsp;|&nbsp;
                    📊 {rec['fractional_shares']:.4f} shares &nbsp;|&nbsp;
                    📈 3M Return: {rec['return_3m']}% &nbsp;|&nbsp;
                    🌡️ Volatility: {rec['volatility']:.1f}%
                </p>
                <p style="color: rgba(200,200,230,0.5); font-size: 0.82rem; margin-top: 6px; line-height: 1.5;">
                    💡 {rec['reason']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # ---- JSON Export ----
        with st.expander("📤 Export Recommendations as JSON"):
            json_out = export_recommendations_json(recs)
            st.code(json_out[:3000] + "\n... (truncated)", language="json")
            st.download_button(
                "⬇️ Download Full JSON",
                json_out,
                file_name=f"weekly_recs_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

        # ---- Disclaimer ----
        st.markdown("""
        ---
        <p style="color: rgba(200,200,230,0.4); font-size: 0.8rem; text-align: center;">
        ⚠️ <strong>Disclaimer:</strong> These recommendations are for educational purposes only.
        Past performance does not guarantee future results. Always do your own research before investing.
        This tool does not constitute financial advice.
        </p>
        """, unsafe_allow_html=True)


# ============================================================================
# TAB 3: MODEL PORTFOLIOS & DCA SIMULATOR
# ============================================================================

def model_portfolio_tab():
    """Model Portfolios & DCA Simulator Tab"""
    inject_custom_css()

    st.markdown("## 🏗️ Model Portfolios & DCA Simulator")
    st.markdown("""
    <p style="color: rgba(200,200,230,0.7); font-size: 1.05rem; margin-bottom: 24px;">
    Choose a pre-built model portfolio or build your own. Simulate dollar-cost averaging
    with historical data and project future compound growth.
    </p>
    """, unsafe_allow_html=True)

    engine = GlobalResearchEngine()
    builder = ModelPortfolioBuilder(engine)

    # ---- Sidebar ----
    with st.sidebar:
        st.markdown("### 🏗️ Portfolio & DCA Settings")

        weekly_budget_portfolio = st.slider(
            "Weekly Contribution ($)",
            min_value=50, max_value=500, value=200, step=25,
            key="portfolio_weekly_budget"
        )

        selected_portfolio = st.selectbox(
            "Model Portfolio",
            builder.get_portfolio_names(),
            help="Choose a pre-built portfolio template"
        )

    # ---- Portfolio Template Preview ----
    template = builder.get_portfolio_template(selected_portfolio)
    if template:
        render_section_header(f"{selected_portfolio}")

        st.markdown(f"""
        <div class="portfolio-template-card">
            <p style="color: rgba(200,200,230,0.8); font-size: 1rem; margin: 0 0 12px 0;">
                {template['description']}
            </p>
            <div style="display: flex; gap: 24px;">
                <div>
                    <span style="color: rgba(200,200,230,0.5); font-size: 0.85rem;">Target Return</span>
                    <p style="color: #00d4aa; font-size: 1.1rem; font-weight: 600; margin: 2px 0;">
                        {template['target_return']}
                    </p>
                </div>
                <div>
                    <span style="color: rgba(200,200,230,0.5); font-size: 0.85rem;">Risk Level</span>
                    <p style="color: #ffd93d; font-size: 1.1rem; font-weight: 600; margin: 2px 0;">
                        {template['risk_level']}
                    </p>
                </div>
                <div>
                    <span style="color: rgba(200,200,230,0.5); font-size: 0.85rem;">Holdings</span>
                    <p style="color: #667eea; font-size: 1.1rem; font-weight: 600; margin: 2px 0;">
                        {len(template['holdings'])} Assets
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Show holdings preview
        holdings_df = pd.DataFrame([
            {
                "Ticker": ticker,
                "Weight": f"{config['weight']*100:.0f}%",
                "Role": config["role"],
                "Weekly $": f"${weekly_budget_portfolio * config['weight']:.2f}",
            }
            for ticker, config in template["holdings"].items()
        ])
        st.dataframe(holdings_df, use_container_width=True, hide_index=True)

    # ---- Build with Live Data ----
    build_col, sim_col = st.columns(2)

    with build_col:
        if st.button("📊 Build with Live Data", type="primary", use_container_width=True):
            progress = st.progress(0, text="Building portfolio...")

            def update_progress(pct, text):
                progress.progress(min(pct, 1.0), text=text)

            with st.spinner("Fetching live market data..."):
                portfolio_data = builder.build_portfolio_with_live_data(
                    selected_portfolio,
                    weekly_budget=weekly_budget_portfolio,
                    progress_callback=update_progress
                )

            progress.empty()

            if "error" in portfolio_data:
                st.error(portfolio_data["error"])
                return

            st.session_state["built_portfolio"] = portfolio_data

    # Display built portfolio
    if "built_portfolio" in st.session_state:
        pd_data = st.session_state["built_portfolio"]

        render_section_header("📊 Live Portfolio Analysis")

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            render_metric_card("Weekly Investment",
                             f"${pd_data['total_weekly_investment']:.2f}",
                             f"${pd_data['annual_projection']:,.0f}/year")
        with mcol2:
            render_metric_card("Portfolio Score",
                             f"{pd_data['portfolio_composite_score']:.0f}/100",
                             "Weighted average")
        with mcol3:
            render_metric_card("Avg Volatility",
                             f"{pd_data['avg_volatility']:.1f}%",
                             "30-day annualized")
        with mcol4:
            render_metric_card("5-Year Projection",
                             format_currency(pd_data['5yr_projection_mid']),
                             "@ moderate return")

        # Holdings table
        if pd_data.get("holdings"):
            hdf = pd.DataFrame(pd_data["holdings"])
            display_cols = [
                "ticker", "name", "role", "weight_pct", "weekly_amount",
                "current_price", "composite_score", "rating",
                "return_3m", "volatility_30d", "trend_strength"
            ]
            available = [c for c in display_cols if c in hdf.columns]
            st.dataframe(
                hdf[available].style.background_gradient(
                    subset=["composite_score"], cmap="YlGn"
                ).format({
                    "weight_pct": "{:.1f}%",
                    "weekly_amount": "${:.2f}",
                    "current_price": "${:.2f}",
                    "return_3m": "{:.1f}%",
                    "volatility_30d": "{:.1f}%",
                }),
                use_container_width=True,
                hide_index=True
            )

            # Weight allocation chart
            fig = go.Figure(data=[go.Pie(
                labels=[h["ticker"] for h in pd_data["holdings"]],
                values=[h["weight_pct"] for h in pd_data["holdings"]],
                hole=0.4,
                textinfo='label+percent',
                hovertemplate="<b>%{label}</b><br>Weight: %{percent}<br>Score: %{customdata[0]}/100<extra></extra>",
                customdata=[[h["composite_score"]] for h in pd_data["holdings"]],
            )])
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                title="Portfolio Weight Allocation",
                font=dict(color='rgba(200,200,230,0.8)'),
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # GROWTH PROJECTIONS
    # ============================================================
    render_section_header("📈 Compound Growth Projections")

    proj_col1, proj_col2 = st.columns([1, 1])
    with proj_col1:
        proj_years = st.slider("Projection Period (years)", 1, 30, 10, key="proj_years")
    with proj_col2:
        existing_balance = st.number_input("Existing Balance ($)", 0, 1000000, 0, step=1000,
                                           key="existing_balance")

    scenarios = GrowthProjector.project_multiple_scenarios(
        weekly_budget_portfolio, proj_years, existing_balance
    )

    # Growth projection chart
    fig = go.Figure()
    colors = {"Conservative (6%)": "#00d4aa", "Moderate (10%)": "#667eea",
              "Aggressive (14%)": "#764ba2", "Optimistic (18%)": "#ff6b6b"}

    for scenario_name, data in scenarios.items():
        projections = data["projections"]
        fig.add_trace(go.Scatter(
            x=[p["year"] for p in projections],
            y=[p["portfolio_value"] for p in projections],
            name=scenario_name,
            mode='lines+markers',
            line=dict(color=colors.get(scenario_name, "#aaa"), width=3),
            fill='tonexty' if scenario_name != "Conservative (6%)" else None,
        ))

    # Add contributions line
    first_scenario = list(scenarios.values())[0]
    fig.add_trace(go.Scatter(
        x=[p["year"] for p in first_scenario["projections"]],
        y=[p["total_contributions"] for p in first_scenario["projections"]],
        name="Total Contributions",
        mode='lines',
        line=dict(color='rgba(255,255,255,0.3)', width=2, dash='dash'),
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=f"Projected Growth: ${weekly_budget_portfolio}/week over {proj_years} years",
        xaxis_title="Year",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified',
        height=500,
        font=dict(color='rgba(200,200,230,0.8)'),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary boxes
    summary_cols = st.columns(len(scenarios))
    for idx, (name, data) in enumerate(scenarios.items()):
        with summary_cols[idx]:
            growth_pct = ((data["final_value"] / data["total_contributions"]) - 1) * 100 if data["total_contributions"] > 0 else 0
            st.markdown(f"""
            <div class="projection-highlight">
                <p style="color: rgba(200,200,230,0.6); font-size: 0.8rem; margin: 0;">{name}</p>
                <p style="color: #667eea; font-size: 1.5rem; font-weight: 700; margin: 4px 0;">
                    {format_currency(data['final_value'])}
                </p>
                <p style="color: #00d4aa; font-size: 0.85rem; margin: 0;">
                    +{format_currency(data['total_growth'])} growth ({growth_pct:.0f}%)
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # DCA BACKTEST
    # ============================================================
    render_section_header("⏪ DCA Historical Backtest")

    st.markdown("""
    <p style="color: rgba(200,200,230,0.5); font-size: 0.9rem;">
    See how your weekly DCA strategy would have performed historically with real market data.
    </p>
    """, unsafe_allow_html=True)

    bt_col1, bt_col2 = st.columns(2)
    with bt_col1:
        bt_start = st.date_input("Backtest Start", value=datetime(2020, 1, 1), key="bt_start")
    with bt_col2:
        bt_end = st.date_input("Backtest End", value=datetime.now(), key="bt_end")

    if st.button("⏪ Run DCA Backtest", use_container_width=True):
        # Get portfolio weights from template
        if template and template.get("holdings"):
            portfolio_weights = {t: c["weight"] for t, c in template["holdings"].items()}
        else:
            portfolio_weights = {"VTI": 0.40, "QQQ": 0.30, "VWO": 0.15, "BND": 0.15}

        simulator = DCASimulator()
        progress = st.progress(0, text="Running backtest...")

        def update_progress(pct, text):
            progress.progress(min(pct, 1.0), text=text)

        with st.spinner("Simulating DCA..."):
            results = simulator.simulate_dca(
                portfolio_weights,
                weekly_budget=weekly_budget_portfolio,
                start_date=bt_start.strftime("%Y-%m-%d"),
                end_date=bt_end.strftime("%Y-%m-%d"),
                progress_callback=update_progress,
            )

        progress.empty()

        if "error" in results:
            st.error(results["error"])
            return

        summary = results["summary"]

        # Summary cards
        scol1, scol2, scol3, scol4 = st.columns(4)
        with scol1:
            render_metric_card("Total Invested",
                             format_currency(summary["total_invested"]),
                             f"{summary.get('total_invested', 0) / 52 / weekly_budget_portfolio:.1f} years" if weekly_budget_portfolio > 0 else "")
        with scol2:
            render_metric_card("Final Value",
                             format_currency(summary["final_portfolio_value"]),
                             f"CAGR: {summary['cagr_pct']}%",
                             summary["cagr_pct"] > 0)
        with scol3:
            gain = summary["total_gain_loss"]
            render_metric_card("Total Gain/Loss",
                             format_currency(gain),
                             f"{summary['total_return_pct']}%",
                             gain > 0)
        with scol4:
            render_metric_card("Positions", str(summary["num_positions"]),
                             "Holdings")

        # Portfolio value over time chart
        weekly_history = results.get("weekly_history", [])
        if weekly_history:
            fig = go.Figure()
            dates = [w["date"] for w in weekly_history]
            values = [w["portfolio_value"] for w in weekly_history]
            invested = [w["total_invested"] for w in weekly_history]

            fig.add_trace(go.Scatter(
                x=dates, y=values,
                name="Portfolio Value",
                line=dict(color="#667eea", width=3),
                fill='tozeroy',
                fillcolor='rgba(102,126,234,0.1)',
            ))
            fig.add_trace(go.Scatter(
                x=dates, y=invested,
                name="Total Invested",
                line=dict(color='rgba(255,255,255,0.3)', width=2, dash='dash'),
            ))

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title="DCA Backtest: Portfolio Value vs Total Invested",
                xaxis_title="Date",
                yaxis_title="Value ($)",
                hovermode='x unified',
                height=450,
                font=dict(color='rgba(200,200,230,0.8)'),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Holdings breakdown
        holdings = results.get("holdings", [])
        if holdings:
            render_section_header("📋 Final Holdings Breakdown")
            hdf = pd.DataFrame(holdings)
            st.dataframe(
                hdf.style.background_gradient(
                    subset=["return_pct"], cmap="RdYlGn"
                ).format({
                    "avg_cost_per_share": "${:.2f}",
                    "current_price": "${:.2f}",
                    "cost_basis": "${:,.2f}",
                    "market_value": "${:,.2f}",
                    "unrealized_gain": "${:,.2f}",
                    "return_pct": "{:.1f}%",
                    "weight_actual": "{:.1f}%",
                    "weight_target": "{:.1f}%",
                }),
                use_container_width=True,
                hide_index=True
            )
