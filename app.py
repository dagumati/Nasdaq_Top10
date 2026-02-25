"""
Main Streamlit Application
===========================
Integrates:
  1. Nasdaq Rotation Strategy (original)
  2. GT/OR Strategic Asset Selector (original)
  3. Global Market Screener (NEW)
  4. Weekly Investment Recommendations (NEW)
  5. Model Portfolios & DCA Simulator (NEW)
"""

import streamlit as st

# Original modules
from nasdaq_rotation_module import nasdaq_rotation_tab
from gtor_selector_module import gtor_asset_selector_tab

# New global research modules
from global_research_dashboard import (
    global_screener_tab,
    weekly_recommendations_tab,
    model_portfolio_tab,
)


def main():
    """Main application with tab-based navigation"""

    st.set_page_config(
        page_title="Global Investment Research Platform",
        layout="wide",
        page_icon="🌍",
        initial_sidebar_state="expanded",
    )

    # ---- Sidebar Branding ----
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 16px 0 24px 0;">
        <h2 style="margin: 0; color: #667eea;">🌍 Global Investor</h2>
        <p style="color: rgba(200,200,230,0.5); font-size: 0.85rem; margin: 4px 0 0 0;">
            AI-Powered Investment Research
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Create Tabs ----
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌍 Global Screener",
        "💰 Weekly Recommendations",
        "🏗️ Model Portfolios & DCA",
        "📊 Nasdaq Rotation",
        "🎯 GT/OR Asset Selector",
    ])

    # ============================================================
    # TAB 1: Global Market Screener (NEW)
    # ============================================================
    with tab1:
        global_screener_tab()

    # ============================================================
    # TAB 2: Weekly Investment Recommendations (NEW)
    # ============================================================
    with tab2:
        weekly_recommendations_tab()

    # ============================================================
    # TAB 3: Model Portfolios & DCA Simulator (NEW)
    # ============================================================
    with tab3:
        model_portfolio_tab()

    # ============================================================
    # TAB 4: Nasdaq Rotation Strategy (ORIGINAL)
    # ============================================================
    with tab4:
        nasdaq_rotation_tab()

    # ============================================================
    # TAB 5: GT/OR Strategic Asset Selector (ORIGINAL)
    # ============================================================
    with tab5:
        gtor_asset_selector_tab()


if __name__ == "__main__":
    main()
