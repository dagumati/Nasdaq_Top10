"""
GT/OR Strategic Asset Selector Module
Provides Game Theory and Operations Research based asset selection interface with real-time data
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px


def fetch_real_time_data(symbol: str) -> dict:
    """Fetch real-time market data and calculate analysis metrics"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current info
        info = ticker.info
        
        # Get historical data (1 year for analysis)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            return None
        
        # Calculate technical indicators
        current_price = hist['Close'].iloc[-1]
        returns = hist['Close'].pct_change().dropna()
        
        # Volatility (annualized)
        volatility = returns.std() * np.sqrt(252) * 100
        
        # Momentum (3-month return)
        momentum_3m = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-63]) - 1) * 100 if len(hist) >= 63 else 0
        
        # Moving averages
        ma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else current_price
        ma_200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else current_price
        
        # Trend strength
        trend_strength = ((current_price - ma_200) / ma_200) * 100 if ma_200 > 0 else 0
        
        # Volume analysis
        avg_volume = hist['Volume'].mean()
        recent_volume = hist['Volume'].iloc[-5:].mean()
        volume_ratio = (recent_volume / avg_volume) if avg_volume > 0 else 1
        
        # Market regime classification
        regime = classify_market_regime(volatility, momentum_3m, trend_strength, volume_ratio)
        
        # Game theory model
        model = determine_game_theory_model(volatility, trend_strength, volume_ratio)
        
        # Strategic Vulnerability Index (SVI)
        svi = calculate_svi(volatility, momentum_3m, volume_ratio, returns)
        
        # Trading recommendations
        action, confidence = determine_trading_action(current_price, ma_50, ma_200, momentum_3m, svi)
        
        # Target prices
        support = hist['Low'].iloc[-20:].min()
        resistance = hist['High'].iloc[-20:].max()
        target_low = support * 0.98
        target_high = resistance * 1.02
        
        # Options recommendations
        strike_price = round(current_price * 1.05 / 5) * 5  # Round to nearest 5
        
        # Portfolio allocation based on confidence and risk
        allocation = calculate_optimal_allocation(confidence, svi, volatility)
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'volatility': volatility,
            'momentum_3m': momentum_3m,
            'regime': regime,
            'model': model,
            'svi': int(svi),
            'action': action,
            'confidence': confidence,
            'target_low': target_low,
            'target_high': target_high,
            'strike_price': int(strike_price),
            'allocation': allocation,
            'ma_50': ma_50,
            'ma_200': ma_200,
            'volume_ratio': volume_ratio
        }
        
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None


def classify_market_regime(volatility: float, momentum: float, trend: float, volume_ratio: float) -> str:
    """Classify the market regime based on indicators"""
    if volatility > 40:
        if volume_ratio > 1.5:
            return "High Volatility Crisis: Information Cascade Event"
        else:
            return "Turbulent Regime: High Uncertainty & Mean Reversion"
    elif volatility > 25:
        if abs(momentum) > 10:
            return "Trending Volatile Market: Momentum Dominates"
        else:
            return "Mixed Signals: Competing Strategies (Game of Coordination)"
    else:
        if trend > 10:
            return "Bullish Evolutionary Game: Trend-Following Dominant"
        elif trend < -10:
            return "Bearish Pressure: Defensive Positioning"
        else:
            return "Stable Equilibrium: Low Volatility Quiet Period"


def determine_game_theory_model(volatility: float, trend: float, volume_ratio: float) -> str:
    """Determine the appropriate game theory model"""
    if volatility > 35:
        return "Stochastic Games (High Uncertainty)"
    elif abs(trend) > 15:
        if volume_ratio > 1.3:
            return "Agent-Based Herding Model"
        else:
            return "Differential Games (Optimal Execution)"
    elif volume_ratio < 0.8:
        return "Quiet Period: Nash Equilibrium"
    else:
        return "Evolutionary Stable Strategy (ESS) / Potential Games"


def calculate_svi(volatility: float, momentum: float, volume_ratio: float, returns: pd.Series) -> float:
    """Calculate Strategic Vulnerability Index (0-100)"""
    # Base volatility component (0-40 points)
    vol_component = min(volatility * 1.2, 40)
    
    # Momentum instability (0-25 points)
    momentum_component = min(abs(momentum) * 1.5, 25)
    
    # Volume anomaly (0-20 points)
    volume_component = min(abs(volume_ratio - 1) * 20, 20)
    
    # Tail risk (0-15 points)
    if len(returns) > 20:
        var_95 = returns.quantile(0.05)
        tail_component = min(abs(var_95) * 150, 15)
    else:
        tail_component = 5
    
    svi = vol_component + momentum_component + volume_component + tail_component
    return min(svi, 100)


def determine_trading_action(price: float, ma_50: float, ma_200: float, momentum: float, svi: float) -> tuple:
    """Determine trading action and confidence level"""
    signals = []
    
    # Moving average signals
    if price > ma_50 > ma_200:
        signals.append(('BUY', 0.8))
    elif price < ma_50 < ma_200:
        signals.append(('SELL', 0.8))
    elif price > ma_50 and price < ma_200:
        signals.append(('HOLD', 0.5))
    
    # Momentum signals
    if momentum > 10:
        signals.append(('BUY', 0.7))
    elif momentum < -10:
        signals.append(('SELL', 0.7))
    else:
        signals.append(('HOLD', 0.6))
    
    # SVI adjustment (high risk = lower confidence)
    risk_adjustment = 1 - (svi / 200)  # Max 50% reduction
    
    # Aggregate signals
    buy_score = sum([conf for act, conf in signals if act == 'BUY']) * risk_adjustment
    sell_score = sum([conf for act, conf in signals if act == 'SELL']) * risk_adjustment
    hold_score = sum([conf for act, conf in signals if act == 'HOLD']) * risk_adjustment
    
    if buy_score > max(sell_score, hold_score):
        return ('BUY', min(buy_score, 0.95))
    elif sell_score > max(buy_score, hold_score):
        return ('SELL', min(sell_score, 0.95))
    else:
        return ('HOLD', min(hold_score, 0.95))


def calculate_optimal_allocation(confidence: float, svi: float, volatility: float) -> float:
    """Calculate optimal portfolio allocation percentage"""
    # Base allocation on confidence
    base_allocation = confidence * 15  # Max 15% at full confidence
    
    # Adjust for risk (SVI and volatility)
    risk_factor = 1 - (svi / 150) - (volatility / 100)
    risk_factor = max(risk_factor, 0.2)  # Minimum 20% of base
    
    allocation = base_allocation * risk_factor
    return round(max(min(allocation, 15), 2), 1)  # Between 2% and 15%


def gtor_asset_selector_tab():
    """GT/OR Strategic Asset Selector Tab with Real-Time Data"""
    
    st.title("🎯 GT/OR Strategic Asset Selector")
    st.markdown("""
    **Real-Time Analysis** using Game Theory and Operations Research principles.
    Enter any stock symbol to analyze market regime, strategic vulnerability, and optimal trading policy.
    """)
    
    # Custom CSS
    st.markdown("""
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
        }
        .risk-high { color: #ff4444; font-weight: bold; }
        .risk-medium { color: #ffaa00; font-weight: bold; }
        .risk-low { color: #00ff88; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol = st.text_input(
            "Enter Stock Symbol",
            value="SPY",
            placeholder="e.g., TSLA, AAPL, NVDA, SPY",
            help="Enter any stock ticker symbol listed on US exchanges"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    # Run analysis
    if analyze_button or symbol:
        with st.spinner(f"📊 Fetching real-time data for {symbol.upper()}..."):
            results = fetch_real_time_data(symbol.upper())
        
        if results:
            st.success(f"✅ Analysis complete for **{results['symbol']}**")
            
            # Display current price and basic info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"${results['current_price']:.2f}")
            with col2:
                market_cap_b = results['market_cap'] / 1e9
                st.metric("Market Cap", f"${market_cap_b:.1f}B")
            with col3:
                st.metric("P/E Ratio", f"{results['pe_ratio']:.2f}" if isinstance(results['pe_ratio'], (int, float)) else "N/A")
            with col4:
                st.metric("Volatility", f"{results['volatility']:.1f}%")
            
            st.markdown("---")
            
            # Strategic Intelligence Section
            st.markdown("### ⭐ Strategic Intelligence (GT Engine)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Market Regime Classification:**")
                st.info(results['regime'])
            
            with col2:
                st.markdown("**Dominant Game Theory Model:**")
                st.info(results['model'])
            
            st.markdown("---")
            
            # Strategic Vulnerability Index (SVI)
            st.markdown("### 🛡️ Strategic Vulnerability Index (SVI)")
            
            svi = results['svi']
            
            # Color coding based on SVI
            if svi > 75:
                svi_color = "risk-high"
                svi_text = "🔴 High Endogenous Risk: Market dynamics are far from an ESS (Evolutionarily Stable Strategy), suggesting vulnerability to sudden, collective behavioral shifts (Reflexivity). Optimal policy must be strictly followed."
                progress_color = "red"
            elif svi > 50:
                svi_color = "risk-medium"
                svi_text = "🟡 Moderate Endogenous Risk: Adaptive agents are causing minor volatility clustering. Proceed with caution."
                progress_color = "orange"
            else:
                svi_color = "risk-low"
                svi_text = "🟢 Low Endogenous Risk: The market is near an Evolutionary Stable Strategy. High confidence in the prescriptive policy."
                progress_color = "green"
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"<h1 class='{svi_color}'>{svi}%</h1>", unsafe_allow_html=True)
            with col2:
                st.progress(svi / 100)
                st.caption(svi_text)
            
            st.markdown("---")
            
            # Trading Recommendations
            st.markdown("### 💼 Prescriptive Policy (π*(s,t)) & Risk")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 Position Trading (Multi-Week/Month)")
                
                # Action with color coding
                action = results['action']
                if action == "BUY":
                    st.markdown(f"**Action:** <span style='color: #00ff88; font-size: 24px'>🟢 {action}</span>", unsafe_allow_html=True)
                elif action == "SELL":
                    st.markdown(f"**Action:** <span style='color: #ff4444; font-size: 24px'>🔴 {action}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**Action:** <span style='color: #ffaa00; font-size: 24px'>🟡 {action}</span>", unsafe_allow_html=True)
                
                st.markdown(f"**Confidence Level:** {results['confidence']*100:.1f}%")
                st.markdown(f"**Optimal Size:** {results['allocation']}% of portfolio")
                st.markdown(f"**Target Range:** ${results['target_low']:.2f} - ${results['target_high']:.2f}")
                
                # Time horizon based on volatility
                if results['volatility'] > 30:
                    time_horizon = "4-6 Weeks (High Vol)"
                elif results['volatility'] > 20:
                    time_horizon = "6-8 Weeks (Moderate Vol)"
                else:
                    time_horizon = "8-12 Weeks (Low Vol)"
                
                st.markdown(f"**Time Horizon:** {time_horizon}")
            
            with col2:
                st.markdown("#### 📊 Options Trading (Leveraged Strategy)")
                
                # Options recommendation
                if action == "BUY":
                    option_type = "CALL Option"
                    option_color = "#00ff88"
                elif action == "SELL":
                    option_type = "PUT Option"
                    option_color = "#ff4444"
                else:
                    option_type = "Neutral Strategy (Iron Condor)"
                    option_color = "#ffaa00"
                
                st.markdown(f"**Recommended Option:** <span style='color: {option_color}'>{option_type}</span>", unsafe_allow_html=True)
                st.markdown(f"**Optimal Strike:** ${results['strike_price']}")
                
                # Expiry based on SVI
                if svi > 70:
                    expiry = "Next 1-2 Monthly Cycles (Near-term)"
                elif svi > 40:
                    expiry = "Next 2-3 Monthly Cycles (Medium-term)"
                else:
                    expiry = "Next 3-4 Monthly Cycles (Longer-term)"
                
                st.markdown(f"**Recommended Expiry:** {expiry}")
                st.warning("⚠️ Note: Use limited capital allocation due to high SVI/endogenous risk. Options carry significant risk.")
            
            st.markdown("---")
            
            # Technical Analysis Chart
            st.markdown("### 📉 Technical Analysis")
            
            try:
                # Fetch historical data for chart
                ticker = yf.Ticker(results['symbol'])
                hist = ticker.history(period="6mo")
                
                if not hist.empty:
                    fig = go.Figure()
                    
                    # Candlestick chart
                    fig.add_trace(go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name='Price'
                    ))
                    
                    # Add moving averages
                    ma_50_series = hist['Close'].rolling(50).mean()
                    ma_200_series = hist['Close'].rolling(200).mean()
                    
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=ma_50_series,
                        mode='lines',
                        name='MA 50',
                        line=dict(color='orange', width=1)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=ma_200_series,
                        mode='lines',
                        name='MA 200',
                        line=dict(color='blue', width=1)
                    ))
                    
                    fig.update_layout(
                        title=f"{results['symbol']} - 6 Month Price Action with Moving Averages",
                        yaxis_title="Price ($)",
                        xaxis_title="Date",
                        template="plotly_dark",
                        height=500,
                        xaxis_rangeslider_visible=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not generate chart: {e}")
            
            # Key Metrics Summary
            st.markdown("### 📊 Key Technical Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("3-Month Momentum", f"{results['momentum_3m']:.2f}%")
                st.metric("50-Day MA", f"${results['ma_50']:.2f}")
            
            with col2:
                st.metric("Annualized Volatility", f"{results['volatility']:.2f}%")
                st.metric("200-Day MA", f"${results['ma_200']:.2f}")
            
            with col3:
                st.metric("Volume Ratio", f"{results['volume_ratio']:.2f}x")
                trend = "Bullish" if results['current_price'] > results['ma_200'] else "Bearish"
                st.metric("Trend vs MA200", trend)
            
            # Disclaimer
            st.markdown("---")
            st.caption("""
            **Disclaimer:** This analysis is for educational and informational purposes only. 
            It does not constitute financial advice. Always conduct your own research and consult 
            with a qualified financial advisor before making investment decisions. Past performance 
            does not guarantee future results.
            """)
        
        else:
            st.error(f"❌ Could not fetch data for {symbol.upper()}. Please check the ticker symbol and try again.")
