from data_loader import DataLoad
from backtester import Backtester
from optimizer import Optimizer
import visualization as viz
import pandas as pd


FILE_PATH = 'data/USDJPY=X-365D-1H.csv' 
MIN_TRADES = 30   
# ==========================================

def run_auto_pilot():
    print(f"--- 1. Loading Data: {FILE_PATH} ---")
    try:
        loader = DataLoad(FILE_PATH)
        df = loader.process_data()
        print(f"Successfully loaded {len(df)} candles.")
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\n--- 2. Running Optimization (Finding Best Params) ---")
    opt = Optimizer(df)
    results = opt.optimize() 

    if results.empty:
        print("No trades generated.")
        return

    valid_results = results[results['Total Trades'] >= MIN_TRADES].copy()
    
    if valid_results.empty:
        print(f"Optimization finished, but no strategy met the {MIN_TRADES} trades requirement.")
        return

    print("\n======= 🏆 TOP 10 CONFIGURATIONS 🏆 =======")
    
    top_results = valid_results.sort_values('Total Profit ($)', ascending=False)
    
    cols_to_show = [
        'Total Profit ($)', 'Max Drawdown ($)', 'Profit Factor', 'Win Rate (%)', 
        'sl_multiplier', 'tp_multiplier', 'be_multiplier',
        'sma_fast', 'sma_slow', 'bb_std'
    ]
    print(top_results.head(10)[cols_to_show].to_string(index=False))
    
    # viz.plot_optimization_race(df, top_results, Backtester, top_n=50)
    
    best_row = top_results.iloc[0]
    best_params = best_row.to_dict()
    
    print("\n--- 3. Auto-Selecting Champion ---")
    print(f"Selected Strategy Profit: ${best_params['Total Profit ($)']}")
    
    if best_params['be_multiplier'] >= 50:
        print("Decision: Break-Even is OFF")
    else:
        print(f"Decision: Break-Even is ON (Trigger at {best_params['be_multiplier']} ATR)")

    print(f"Running Re-Test for Charting...")

    champion_bot = Backtester(df, params=best_params, position_size=1000)
    final_metrics = champion_bot.run_backtest()
    
    champion_bot.print_summary()
    
    if not champion_bot.trade_log.empty:
        print("\n📜 Sample Trades (First 5):")
        log_cols = ['entry_time', 'trade_type', 'pnl_usd', 'duration']
        print(champion_bot.trade_log[log_cols].head(5).to_string(index=False))

        viz.plot_performance(df, champion_bot.trade_log, final_metrics)
    else:
        print("No trades to plot.")

if __name__ == "__main__":
    run_auto_pilot()