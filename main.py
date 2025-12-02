from data_loader import DataLoad
from backtester import Backtester
from optimizer import Optimizer
import visualization as viz
import json 

# ==========================================
FILE_PATH = 'data/EURUSD-365D-1H.csv'
MIN_TRADES = 30  
PARAMS_FILE = "best_params.json"
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

    print("\n--- 2. Running Optimization ---")
    opt = Optimizer(df)
    results = opt.optimize() 

    if results.empty:
        print("No trades generated.")
        return

    valid_results = results[results['Total Trades'] >= MIN_TRADES].copy()
    
    if valid_results.empty:
        print(f"Optimization finished, but no strategy met the requirements.")
        return

    print("\n======= 🏆 TOP 10 CONFIGURATIONS 🏆 =======")
    top_results = valid_results.sort_values('Total Profit ($)', ascending=False)
    
    cols_to_show = [
        'Total Profit ($)', 'Max Drawdown ($)', 'Profit Factor', 'Win Rate (%)', 
        'sl_multiplier', 'tp_multiplier', 'be_multiplier',
        'sma_fast', 'sma_slow'
    ]
    print(top_results.head(10)[cols_to_show].to_string(index=False))
    
    best_row = top_results.iloc[0]
    best_params = best_row.to_dict()
    
    clean_params = {k: v for k, v in best_params.items() if k in [
        'sma_fast', 'sma_slow', 'sma_trend', 'bb_period', 'bb_std', 
        'atr_period', 'range_atr_filter', 'sl_multiplier', 'tp_multiplier', 'be_multiplier'
    ]}

    print("\n--- 3. Saving Champion to File ---")
    print(f"Selected Strategy Profit: ${best_params['Total Profit ($)']}")
    
    with open(PARAMS_FILE, "w") as f:
        json.dump(clean_params, f, indent=4)
    print(f"✅ Saved parameters to '{PARAMS_FILE}'. Live bot will use this!")

    print(f"Running Re-Test for Charting...")
    champion_bot = Backtester(df, params=clean_params, position_size=1000)
    final_metrics = champion_bot.run_backtest()
    champion_bot.print_summary()
    
    if not champion_bot.trade_log.empty:
        viz.plot_performance(df, champion_bot.trade_log, final_metrics)

if __name__ == "__main__":
    run_auto_pilot()