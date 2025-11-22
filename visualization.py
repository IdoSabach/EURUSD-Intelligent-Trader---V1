import matplotlib.pyplot as plt
import pandas as pd

def plot_performance(df, trade_log, metrics):
    """
    מצייר גרף של הביצועים: מחיר, בולינגר, ועסקאות.
    """
    print("Loading chart...")
    plt.figure(figsize=(16, 8))
    
    # 1. ציור המחיר
    plt.plot(df.index, df['price'], label='Price', color='black', alpha=0.6, linewidth=1)
    
    # 2. ציור בולינגר (להמחשה)
    ma = df['price'].rolling(20).mean()
    sd = df['price'].rolling(20).std()
    plt.plot(df.index, ma + 2*sd, color='green', alpha=0.15, linestyle='--')
    plt.plot(df.index, ma - 2*sd, color='red', alpha=0.15, linestyle='--')

    # 3. ציור הטריידים
    if not trade_log.empty:
        wins = trade_log[trade_log['pnl_usd'] > 0]
        losses = trade_log[trade_log['pnl_usd'] <= 0]
        
        # כניסות מרוויחות (חץ ירוק)
        plt.scatter(wins['entry_time'], wins['entry_price'], c='green', marker='^', s=100, label='Win Entry', zorder=5)
        # כניסות מפסידות (חץ אדום)
        plt.scatter(losses['entry_time'], losses['entry_price'], c='red', marker='v', s=100, label='Loss Entry', zorder=5)
        # יציאות (איקס כחול)
        plt.scatter(trade_log['exit_time'], trade_log['exit_price'], c='blue', marker='x', s=40, alpha=0.7, label='Exit')

    # כותרת ועיצוב
    pf = metrics.get('Profit Factor', 0)
    profit = metrics.get('Total Profit ($)', 0)
    wr = metrics.get('Win Rate (%)', 0)
    
    title_str = f"FINAL RESULT: Profit ${profit} | PF: {pf} | WinRate: {wr}%"
    plt.title(title_str, fontsize=14, fontweight='bold')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.show()