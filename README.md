# 📈 Momentum + Low Volatility Strategy (QuantConnect / LEAN)

## Overview

This project implements a **systematic equity strategy** combining:

- **12–1 Momentum**
- **Low Volatility**

The strategy is built and backtested using the **QuantConnect LEAN engine** and follows a practitioner-style pipeline:

> Signal → Ranking → Portfolio Construction → Execution

---

## Strategy Description

At each monthly rebalance:

### 1. Universe Selection
- Top ~500 US equities by dollar volume
- Price > $10
- Fundamental data available

---

### 2. Signal Construction

#### Momentum (12–1)
\[
\text{Momentum}_i = \frac{P_{t-1m}}{P_{t-12m}} - 1
\]

- Uses 12 months of history  
- Skips the most recent month to avoid short-term reversal  

---

#### Volatility (6-month realized)
\[
\sigma_i = \sqrt{252} \cdot \text{std}(r_{t-6m:t})
\]

- Based on daily returns over the past 6 months  

---

### 3. Cross-sectional Normalization

Signals are converted to **percentile ranks**:

- Momentum → higher is better  
- Volatility → lower is better (inverted)  

---

### 4. Composite Score

\[
\text{Score}_i =
0.5 \cdot \text{Rank}(\text{Momentum}_i)
+
0.5 \cdot \text{Rank}(-\sigma_i)
\]

---

### 5. Portfolio Construction

- Select top **20 stocks**
- Equal-weight allocation
- Monthly rebalancing

---

### 6. Optional Regime Filter

- Invest only if:
\[
\text{SPY} > \text{200-day moving average}
\]

- Otherwise move to cash

---

## Key Features

- Fully systematic cross-sectional strategy  
- Uses only QuantConnect available data  
- Robust rank-based normalization  
- Monthly rebalancing  
- Clean separation between signal and execution  

---

## Project Structure
quantconnect-momentum-lowvol/
├── main.py
├── README.md
└── research/

---

## How to Run

### QuantConnect Cloud

1. Create a new project on QuantConnect  
2. Replace `main.py` with this repository code  
3. Run backtest  

---

## Results Interpretation

This is a **long-only strategy**, so:

- Returns are largely driven by **market exposure**
- Signals mainly create **tilts**, not pure alpha

### Important Insight

> A strategy can appear to have alpha vs the market but be fully explained by factor exposures.

---

## Limitations

- Long-only (not market-neutral)  
- No transaction costs or slippage  
- No sector constraints  
- Equal-weight portfolio (no optimization)  
- Uses well-known factors (crowded)  

---

## Extensions

### Signal Improvements
- Residual momentum  
- Beta-adjusted volatility  
- Add value / quality  

### Portfolio Construction
- Risk-adjusted weights  
- Mean-variance optimization  
- Sector neutrality  

### Risk Management
- Volatility targeting  
- Drawdown control  

### Research
- Factor regression (FF + MOM + LOWVOL)  
- Performance attribution  

---

## Key Concepts

- Cross-sectional factor investing  
- Signal normalization  
- Portfolio construction vs factor exposure  
- Event-driven backtesting  

---

## Author

Stefano Grillini  

---

## Disclaimer

For research and educational purposes only.  
Not investment advice.