# 🚀 Algo-Trader Pro: Intelligent Quantitative Trading System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-MetaTrader%205-blue?style=for-the-badge)
![VPS](https://img.shields.io/badge/Deployment-24%2F7%20VPS-blueviolet?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Notifications-Telegram%20Bot-2ca5e0?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live%20Production-brightgreen?style=for-the-badge)

**Algo-Trader Pro** is a comprehensive algorithmic trading suite designed for high-precision execution in Forex and Commodities markets.
The system utilizes a **"Trend Confirmation Hook"** strategy, enhanced by a vectorized NumPy backtesting engine and parallel hyperparameter optimization.

The system is fully deployed on a **cloud VPS** for 24/7 autonomous trading, featuring a robust watchdog mechanism and real-time Telegram monitoring.

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

# 📡 Live Deployment & Monitoring

The system is deployed on a dedicated **Windows VPS** (Contabo) in the London region for ultra-low latency execution.

### 🤖 24/7 Autonomous Operation
* **Watchdog Script:** A custom `.bat` wrapper monitors the bot process. If a crash or disconnect occurs, the bot restarts automatically within 5 seconds.
* **Startup Automation:** Integrated with Windows Task Scheduler to ensure the bot launches automatically upon server reboot.

### 📱 Smart Telegram Integration
The bot communicates directly with the trader via a dedicated Telegram Bot API:
* **🔔 Trade Alerts:** Instant notification on Entry (Buy/Sell) including Price, SL, and TP levels.
* **💓 Hourly Heartbeat:** Sends a status report every hour (XX:00) containing:
    * System Status (Running/Idle)
    * Current Asset Price
    * Account Equity & Balance
* **⚠️ Error Reporting:** Critical exceptions or connection losses are immediately pushed to the user's phone.

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
    
    subgraph Live Trading
    Live(live_trader.py) --> Strategy;
    Live --> Telegram(telegram_notify.py);
    end
    
    Main --> Viz(visualization.py);