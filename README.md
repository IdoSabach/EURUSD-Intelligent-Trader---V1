````markdown
# 🚀 Algo-Trader Pro: Intelligent Quantitative Trading System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production-brightgreen?style=for-the-badge)
![Strategy](https://img.shields.io/badge/Strategy-Trend%20Confirmation-orange?style=for-the-badge)

**Algo-Trader Pro** is a comprehensive algorithmic trading suite designed for high-precision execution in Forex and Commodities markets.
The system utilizes a **"Trend Confirmation Hook"** strategy, enhanced by a vectorized NumPy backtesting engine and parallel hyperparameter optimization.

---

# 🌍 Performance & Parameters by Asset

The following results are based on **Walk-Forward Analysis (WFA)** over a 12-month period using **H1 Timeframes**.
Each asset has been independently optimized to fit its unique volatility signature.

## 🇪🇺 EURUSD (The Stabilizer)
*Characterized by high stability and low drawdown. Ideal for capital preservation.*

### 📊 Performance Metrics
| Metric | Value | Description |
| :--- | :--- | :--- |
| **Profit Factor** | **1.78** 🟢 | High efficiency ratio. |
| **Win Rate** | **38.5%** | Validated by high R:R ratio. |
| **Max Drawdown** | **-6.1%** 🛡️ | Extremely low risk profile. |
| **Avg Win / Avg Loss** | **$25.6 / $12.6** | Winners are **2x** larger than losers. |
| **Total Trades** | ~122 / Year | ~2.5 trades per week. |

### ⚙️ Optimized Configuration (The "Vault")
| Parameter | Value | Logic |
| :--- | :--- | :--- |
| **SMA Fast / Slow** | `15` / `100` | Sensitive trend filter. |
| **SMA Trend** | `200` | Global trend baseline. |
| **Stop Loss (ATR)** | **2.0x** | Tight risk management. |
| **Take Profit (ATR)** | **5.0x** | Extended target seeking. |
| **Break Even** | **OFF** | Strategy performs better without trailing. |

---

## 🇬🇧 GBPUSD (The Accelerator)
*Higher volatility pair with faster execution and active risk mitigation.*

### 📊 Performance Metrics
| Metric | Value | Description |
| :--- | :--- | :--- |
| **Profit Factor** | **1.84** 🟢 | Superior profitability. |
| **Win Rate** | **43.1%** | Higher accuracy than EUR. |
| **Max Drawdown** | **-5.2%** 🛡️ | Lowest drawdown among all assets. |
| **Avg Win / Avg Loss** | **$4.2 / $1.7** | Winners are **2.5x** larger than losers. |
| **Total Trades** | ~109 / Year | Consistent activity. |

### ⚙️ Optimized Configuration (The "Vault")
| Parameter | Value | Logic |
| :--- | :--- | :--- |
| **SMA Fast / Slow** | `40` / `100` | Smoother trend filtration. |
| **SMA Trend** | `200` | Global trend baseline. |
| **Stop Loss (ATR)** | **1.8x** | Very tight stops. |
| **Take Profit (ATR)** | **2.5x** | Moderate targets (High Hit-Rate). |
| **Break Even** | **ON (1.5 ATR)** | **Active protection locks profits early.** |

---

## 🥇 XAUUSD / Gold (The Alpha Generator)
*High-reward asset driven by long-term momentum trends.*

### 📊 Performance Metrics
| Metric | Value | Description |
| :--- | :--- | :--- |
| **Profit Factor** | **2.10** 🏆 | Maximum efficiency. |
| **Win Rate** | **37.3%** | Lower win rate, massive payouts. |
| **Max Drawdown** | **-18.0%** 🔴 | Higher volatility tolerance required. |
| **Avg Win / Avg Loss** | **High Spread** | Winners are **3.5x** larger than losers. |
| **Avg Duration** | **5 Days** | Swing trading profile. |

### ⚙️ Optimized Configuration (The "Vault")
| Parameter | Value | Logic |
| :--- | :--- | :--- |
| **SMA Fast / Slow** | `45` / `140` | Deep trend analysis. |
| **SMA Trend** | `200` | Global trend baseline. |
| **Stop Loss (ATR)** | **2.0x** | Standard risk. |
| **Take Profit (ATR)** | **7.0x** 🚀 | **"Home Run" targeting strategy.** |
| **Break Even** | **OFF** | Allows asset to "breathe" during volatility. |

---

# 🏗️ Technical Architecture

### 📂 Project Structure
```mermaid
graph TD;
    Main(main.py) --> Loader(data_loader.py);
    Main --> Optimizer(optimizer.py);
    Optimizer --> Backtester(backtester.py);
    Main --> Backtester;
    Backtester --> Strategy(strategy.py);
    Strategy --> Indicators(indicators.py);
    Main --> Viz(visualization.py);
````

### 🧩 Module Breakdown

1.  **`data_loader.py`:** Handles ingestion of raw CSV data from MT5/Yahoo, cleans data anomalies, and normalizes timezones.
2.  **`indicators.py`:** A dedicated math library for calculating SMA, Bollinger Bands, and ATR dynamically.
3.  **`strategy.py`:** Encapsulates the **"Hook" Logic** — buying only when price reverts into the bands during a confirmed trend.
4.  **`backtester.py`:** The core engine. Uses **Vectorized NumPy arrays** to simulate years of trading in milliseconds, with intra-bar precision.
5.  **`optimizer.py`:** Utilizes **Parallel Computing (Joblib)** to test thousands of parameter combinations across all CPU cores.
6.  **`visualization.py`:** Generates professional financial charts, including Equity Curves and Trade Entry/Exit mapping.

-----

### 🚀 Usage Guide

1.  **Setup Environment:**
    ```bash
    pip install pandas numpy matplotlib joblib yfinance
    ```
2.  **Prepare Data:**
    Place your `EURUSD_H1.csv` file in the `data/` folder.
3.  **Run Optimization:**
    Set `MODE = 'OPTIMIZE'` in `main.py` and run.
4.  **Run Champion:**
    Set `MODE = 'CHAMPION'` and insert the best parameters to visualize results.

<!-- end list -->

```bash
python main.py
```

-----

**Developed by Ido Sabach** 👨‍💻

```
```