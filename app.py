"""
Main Streamlit Application
Integrates Nasdaq Rotation Strategy and GT/OR Strategic Asset Selector
"""

import streamlit as st

# Import modules
from nasdaq_rotation_module import nasdaq_rotation_tab
from gtor_selector_module import gtor_asset_selector_tab


def main():
    """Main application with tab-based navigation"""
    
    st.set_page_config(
        page_title="Nasdaq Strategy & GT/OR Asset Selector",
        layout="wide",
        page_icon="📈"
    )
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs([
        "📊 Nasdaq Rotation Strategy",
        "🎯 GT/OR Strategic Asset Selector"
    ])
    
    # ============================================================
    # TAB 1: Nasdaq Rotation Strategy
    # ============================================================
    with tab1:
        nasdaq_rotation_tab()
    
    # ============================================================
    # TAB 2: GT/OR Strategic Asset Selector
    # ============================================================
    with tab2:
        gtor_asset_selector_tab()


if __name__ == "__main__":
    main()

