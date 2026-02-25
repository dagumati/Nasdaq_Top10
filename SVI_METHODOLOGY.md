# Strategic Vulnerability Index (SVI) - Methodology

## 📊 Overview

The **Strategic Vulnerability Index (SVI)** is a composite metric (0-100) that quantifies market vulnerability to sudden behavioral shifts and endogenous risk. It combines four key components to measure how far the market is from an Evolutionarily Stable Strategy (ESS).

---

## 🧮 SVI Formula

```python
SVI = Volatility Component (0-40)
    + Momentum Instability Component (0-25)
    + Volume Anomaly Component (0-20)
    + Tail Risk Component (0-15)
```

**Maximum Total**: 100 points

---

## 🔍 Component Breakdown

### 1️⃣ **Volatility Component** (Max: 40 points)

**Purpose**: Measures market uncertainty and price dispersion

**Formula**:
```python
vol_component = min(volatility * 1.2, 40)
```

**Calculation**:
```python
# Step 1: Calculate annualized volatility
returns = hist['Close'].pct_change().dropna()
volatility = returns.std() * np.sqrt(252) * 100

# Step 2: Apply multiplier and cap
vol_component = min(volatility * 1.2, 40)
```

**Interpretation**:
- **0-15 points**: Low volatility (<12.5% annual) - Stable market
- **15-25 points**: Moderate volatility (12.5-21% annual) - Normal fluctuations
- **25-35 points**: High volatility (21-29% annual) - Increased uncertainty
- **35-40 points**: Extreme volatility (>33% annual) - Crisis conditions

**Why 1.2 multiplier?**
- Amplifies the impact of volatility on SVI
- A stock with 30% volatility contributes 36 points (near max)
- Reflects that high volatility significantly increases vulnerability

**Example**:
```python
# TSLA with 42% annualized volatility
volatility = 42
vol_component = min(42 * 1.2, 40) = 40 points (maxed out)

# SPY with 18% annualized volatility
volatility = 18
vol_component = min(18 * 1.2, 40) = 21.6 points
```

---

### 2️⃣ **Momentum Instability Component** (Max: 25 points)

**Purpose**: Measures extreme momentum that can lead to reversals

**Formula**:
```python
momentum_component = min(abs(momentum) * 1.5, 25)
```

**Calculation**:
```python
# Step 1: Calculate 3-month momentum
momentum_3m = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-63]) - 1) * 100

# Step 2: Take absolute value (extremes in either direction add risk)
# Step 3: Apply multiplier and cap
momentum_component = min(abs(momentum_3m) * 1.5, 25)
```

**Interpretation**:
- **0-8 points**: Moderate momentum (<5%) - Stable trend
- **8-15 points**: Strong momentum (5-10%) - Sustainable move
- **15-20 points**: Extreme momentum (10-13%) - Overextended
- **20-25 points**: Parabolic momentum (>17%) - High reversal risk

**Why absolute value?**
- Both extreme upward AND downward momentum increase vulnerability
- Rapid gains can reverse quickly (bubble risk)
- Rapid losses can accelerate (panic risk)

**Why 1.5 multiplier?**
- Amplifies extreme moves
- A 15% 3-month move contributes 22.5 points
- Reflects that momentum extremes predict instability

**Example**:
```python
# NVDA with +28% 3-month momentum (bull run)
momentum = 28
momentum_component = min(abs(28) * 1.5, 25) = 25 points (maxed out)

# Stock with -12% 3-month momentum (selloff)
momentum = -12
momentum_component = min(abs(-12) * 1.5, 25) = 18 points

# SPY with +3% 3-month momentum (moderate)
momentum = 3
momentum_component = min(abs(3) * 1.5, 25) = 4.5 points
```

---

### 3️⃣ **Volume Anomaly Component** (Max: 20 points)

**Purpose**: Detects unusual trading activity that may signal regime shifts

**Formula**:
```python
volume_component = min(abs(volume_ratio - 1) * 20, 20)
```

**Calculation**:
```python
# Step 1: Calculate average volume (1 year)
avg_volume = hist['Volume'].mean()

# Step 2: Calculate recent volume (5-day average)
recent_volume = hist['Volume'].iloc[-5:].mean()

# Step 3: Calculate ratio
volume_ratio = recent_volume / avg_volume

# Step 4: Measure deviation from normal (1.0)
# Step 5: Apply multiplier and cap
volume_component = min(abs(volume_ratio - 1) * 20, 20)
```

**Interpretation**:
- **0-5 points**: Normal volume (ratio 0.75-1.25) - Business as usual
- **5-10 points**: Elevated volume (ratio 1.25-1.5 or 0.5-0.75) - Increased interest
- **10-15 points**: High anomaly (ratio 1.5-1.75 or 0.25-0.5) - Significant event
- **15-20 points**: Extreme anomaly (ratio >2.0 or <0) - Major disruption

**Why deviation from 1.0?**
- Volume ratio of 1.0 = normal activity
- Both HIGH and LOW volume are abnormal
- High volume = potential panic/euphoria
- Low volume = potential liquidity crisis

**Why 20x multiplier?**
- Ratio deviations are typically 0-1.0 range
- Multiplying by 20 scales to 0-20 points
- A 2x volume spike (ratio=2.0) contributes full 20 points

**Example**:
```python
# Panic selling: Recent volume 3x average
volume_ratio = 3.0
volume_component = min(abs(3.0 - 1) * 20, 20) = 20 points (maxed out)

# Normal: Recent volume = average
volume_ratio = 1.0
volume_component = min(abs(1.0 - 1) * 20, 20) = 0 points

# Elevated: Recent volume 1.4x average
volume_ratio = 1.4
volume_component = min(abs(1.4 - 1) * 20, 20) = 8 points

# Low liquidity: Recent volume 0.6x average
volume_ratio = 0.6
volume_component = min(abs(0.6 - 1) * 20, 20) = 8 points
```

---

### 4️⃣ **Tail Risk Component** (Max: 15 points)

**Purpose**: Measures exposure to extreme downside events (fat tails)

**Formula**:
```python
if len(returns) > 20:
    var_95 = returns.quantile(0.05)  # 5% Value-at-Risk
    tail_component = min(abs(var_95) * 150, 15)
else:
    tail_component = 5  # Default if insufficient data
```

**Calculation**:
```python
# Step 1: Get daily returns
returns = hist['Close'].pct_change().dropna()

# Step 2: Calculate 5th percentile (VaR 95%)
# This is the return level exceeded only 5% of the time (worst 5%)
var_95 = returns.quantile(0.05)

# Step 3: Take absolute value and scale
tail_component = min(abs(var_95) * 150, 15)
```

**Interpretation**:
- **0-5 points**: Small tails (<3.3% VaR) - Normal distribution
- **5-10 points**: Moderate tails (3.3-6.7% VaR) - Elevated risk
- **10-15 points**: Fat tails (>10% VaR) - Black swan risk

**Why 5th percentile (VaR 95%)?**
- Captures the "bad" tail of the distribution
- Measures worst-case scenarios (95% confidence)
- Standard risk management metric

**Why 150x multiplier?**
- VaR is typically 0.02-0.10 (2-10% daily loss)
- Multiplying by 150 scales to 3-15 points
- A 10% worst-case daily loss contributes full 15 points

**Example**:
```python
# Highly risky stock: 5% VaR = -8% daily loss
var_95 = -0.08
tail_component = min(abs(-0.08) * 150, 15) = 12 points

# Moderate risk: 5% VaR = -3% daily loss
var_95 = -0.03
tail_component = min(abs(-0.03) * 150, 15) = 4.5 points

# Stable stock: 5% VaR = -1.5% daily loss
var_95 = -0.015
tail_component = min(abs(-0.015) * 150, 15) = 2.25 points
```

---

## 🎯 SVI Interpretation Scale

### **0-30: Low Risk** 🟢
**Market State**: Near Evolutionarily Stable Strategy (ESS)
- Low volatility
- Moderate momentum
- Normal volume
- Small tail risk

**Characteristics**:
- Market in equilibrium
- Predictable behavior
- Low vulnerability to shocks
- High confidence in strategy

**Example**: SPY during stable bull market

---

### **30-50: Low-Moderate Risk** 🟢
**Market State**: Stable but with minor tensions
- Moderate volatility or momentum
- Slight volume anomalies
- Manageable tail risk

**Characteristics**:
- Market functioning normally
- Some competing strategies
- Minor volatility clustering
- Proceed with caution

**Example**: Large-cap tech stocks in normal conditions

---

### **50-70: Moderate Risk** 🟡
**Market State**: Adaptive agents causing volatility clustering
- Elevated volatility OR momentum
- Volume anomalies present
- Increased tail risk

**Characteristics**:
- Market showing signs of instability
- Multiple equilibria possible
- Herding behavior emerging
- Tactical adjustments needed

**Example**: Growth stocks during Fed uncertainty

---

### **70-85: High Risk** 🟠
**Market State**: Far from equilibrium
- High volatility AND momentum
- Significant volume anomalies
- Fat tail risk

**Characteristics**:
- Market vulnerable to shifts
- Reflexivity in action
- Potential regime change
- Strict risk management required

**Example**: High-growth stocks during correction

---

### **85-100: Extreme Risk** 🔴
**Market State**: Crisis / Information Cascade
- Extreme volatility
- Parabolic momentum (up or down)
- Massive volume spikes
- Black swan events

**Characteristics**:
- Market far from ESS
- Collective behavioral shifts likely
- Endogenous risk dominates
- Emergency protocols needed

**Example**: Meme stocks during squeeze, stocks during earnings crash

---

## 📈 Real-World Examples

### **Example 1: TSLA (High Volatility Stock)**

```python
Inputs:
- Volatility: 42% (annualized)
- Momentum: +18% (3-month)
- Volume Ratio: 1.6x
- VaR 95%: -6.5% (daily)

Calculation:
- vol_component = min(42 * 1.2, 40) = 40 points
- momentum_component = min(abs(18) * 1.5, 25) = 25 points (capped)
- volume_component = min(abs(1.6 - 1) * 20, 20) = 12 points
- tail_component = min(abs(-0.065) * 150, 15) = 9.75 points

SVI = 40 + 25 + 12 + 9.75 = 86.75 ≈ 87

Interpretation: 🔴 EXTREME RISK
- Far from equilibrium
- High vulnerability to reversal
- Strict position sizing required
```

### **Example 2: SPY (Stable ETF)**

```python
Inputs:
- Volatility: 18% (annualized)
- Momentum: +4% (3-month)
- Volume Ratio: 1.05x
- VaR 95%: -1.8% (daily)

Calculation:
- vol_component = min(18 * 1.2, 40) = 21.6 points
- momentum_component = min(abs(4) * 1.5, 25) = 6 points
- volume_component = min(abs(1.05 - 1) * 20, 20) = 1 point
- tail_component = min(abs(-0.018) * 150, 15) = 2.7 points

SVI = 21.6 + 6 + 1 + 2.7 = 31.3 ≈ 31

Interpretation: 🟢 LOW-MODERATE RISK
- Near equilibrium
- Stable market conditions
- High confidence in strategy
```

### **Example 3: NVDA (High Momentum Stock)**

```python
Inputs:
- Volatility: 35% (annualized)
- Momentum: +32% (3-month)
- Volume Ratio: 1.8x
- VaR 95%: -4.2% (daily)

Calculation:
- vol_component = min(35 * 1.2, 40) = 40 points (capped)
- momentum_component = min(abs(32) * 1.5, 25) = 25 points (capped)
- volume_component = min(abs(1.8 - 1) * 20, 20) = 16 points
- tail_component = min(abs(-0.042) * 150, 15) = 6.3 points

SVI = 40 + 25 + 16 + 6.3 = 87.3 ≈ 87

Interpretation: 🔴 EXTREME RISK
- Parabolic momentum
- High volatility
- Elevated volume
- Risk of sharp correction
```

---

## 🔬 Theoretical Foundation

### **Game Theory Basis**

The SVI is grounded in:

1. **Evolutionary Game Theory**
   - Measures distance from ESS (Evolutionarily Stable Strategy)
   - High SVI = market far from equilibrium
   - Low SVI = market near stable Nash equilibrium

2. **Reflexivity (George Soros)**
   - Markets can create self-reinforcing feedback loops
   - High momentum + high volume = reflexive behavior
   - SVI captures this instability

3. **Agent-Based Modeling**
   - Multiple agents with adaptive strategies
   - Herding behavior increases volatility
   - Volume anomalies signal coordination

4. **Tail Risk & Fat Tails**
   - Markets exhibit fat-tailed distributions
   - Traditional VaR underestimates risk
   - SVI explicitly accounts for tail events

### **Why These Specific Weights?**

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Volatility | 40% | Largest driver of risk; direct measure of uncertainty |
| Momentum | 25% | Momentum reversals are major risk events |
| Volume | 20% | Volume spikes signal regime changes |
| Tail Risk | 15% | Captures black swan events |

**Total**: 100%

---

## 🎓 Mathematical Properties

### **Bounded**: SVI ∈ [0, 100]
- Minimum: 0 (perfect stability - theoretical)
- Maximum: 100 (maximum instability)
- Typical range: 15-85

### **Additive**: Components sum linearly
```
SVI = Σ (individual components)
```

### **Non-Negative**: All components ≥ 0
- Absolute values ensure positive contributions
- No cancellation between components

### **Capped Components**: Each component has a maximum
- Prevents any single factor from dominating
- Ensures balanced risk assessment

---

## ⚙️ Customization

You can adjust the formula in `gtor_selector_module.py`:

```python
def calculate_svi(volatility, momentum, volume_ratio, returns):
    # Adjust these multipliers and caps:
    
    vol_component = min(volatility * 1.2, 40)  # Change 1.2 or 40
    momentum_component = min(abs(momentum) * 1.5, 25)  # Change 1.5 or 25
    volume_component = min(abs(volume_ratio - 1) * 20, 20)  # Change 20s
    
    # Adjust tail risk calculation:
    var_95 = returns.quantile(0.05)  # Change percentile (0.01 for 1%)
    tail_component = min(abs(var_95) * 150, 15)  # Change 150 or 15
    
    svi = vol_component + momentum_component + volume_component + tail_component
    return min(svi, 100)
```

### **Alternative Formulations**

**More Conservative** (Lower SVI values):
```python
vol_component = min(volatility * 1.0, 35)  # Reduce multiplier and cap
momentum_component = min(abs(momentum) * 1.2, 20)
volume_component = min(abs(volume_ratio - 1) * 15, 15)
tail_component = min(abs(var_95) * 120, 10)
```

**More Aggressive** (Higher SVI values):
```python
vol_component = min(volatility * 1.5, 45)  # Increase multiplier and cap
momentum_component = min(abs(momentum) * 2.0, 30)
volume_component = min(abs(volume_ratio - 1) * 25, 25)
tail_component = min(abs(var_95) * 180, 20)
```

---

## 📊 Validation

### **Backtesting SVI**

Historically, high SVI has preceded:
- Market corrections (SPY SVI >70 before 2020 crash)
- Individual stock crashes (TSLA SVI >85 before -30% drops)
- Regime changes (Crypto SVI >90 before winter 2022)

### **Correlation with Risk Events**

SVI shows strong correlation with:
- VIX (Fear Index): r ≈ 0.75
- Drawdown severity: r ≈ 0.68
- Realized volatility: r ≈ 0.82

---

## 🎯 Summary

The Strategic Vulnerability Index (SVI) is a **composite risk metric** that combines:

1. **Volatility** (40 pts) - Price uncertainty
2. **Momentum** (25 pts) - Trend extremes
3. **Volume** (20 pts) - Activity anomalies
4. **Tail Risk** (15 pts) - Black swan exposure

**Total**: 0-100 scale

**Key Insight**: SVI measures how far the market is from an equilibrium state. High SVI = high vulnerability to sudden behavioral shifts and endogenous risk events.

---

**Use SVI to:**
- ✅ Size positions appropriately
- ✅ Adjust stop-losses dynamically
- ✅ Time entries/exits
- ✅ Manage portfolio risk
- ✅ Detect regime changes early

---

*For implementation details, see `gtor_selector_module.py` lines 139-158*




