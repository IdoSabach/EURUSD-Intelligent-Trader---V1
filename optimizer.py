import pandas as pd
import numpy as np
import itertools
from joblib import Parallel, delayed
from backtester import Backtester

def run_single_backtest_task(df, params):
    try:
        bot = Backtester(df, params=params)
        metrics = bot.run_backtest()
        
        metrics.update(params)
        return metrics
    except Exception as e:
        return None

class Optimizer:
    def __init__(self, df):
        self.df = df

    def get_monster_grid(self):
        """
         numpy ranges.

        """
        return {
            'sma_fast': list(range(5, 50, 5)), 
            'sma_slow': list(range(50, 160, 10)), 
            'sma_trend': [200], 
            'bb_period': [20],
            'bb_std': [round(x, 1) for x in np.arange(2.0, 2.6, 0.2)], 
            'atr_period': [14],
            'range_atr_filter': [0.8],
            'sl_multiplier': [round(x, 1) for x in np.arange(1.5, 3.1, 0.25)],
            'tp_multiplier': [round(x, 1) for x in np.arange(2.0, 7.5, 0.5)],
            'be_multiplier': [1.5, 100.0] 
        }

    def optimize(self):
        param_grid = self.get_monster_grid()
        keys, values = zip(*param_grid.items())
        
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        total = len(combinations)
        print(f"\n--- 🦖 STARTING MONSTER OPTIMIZATION ---")
        print(f"Testing {total:,} combinations using ALL CPU cores.")
        print(f"This allows us to find the EXACT best parameters.")
        print("Processing... (Please wait)\n")
        
        results = Parallel(n_jobs=-1, verbose=1)(
            delayed(run_single_backtest_task)(self.df, params) 
            for params in combinations
        )
        
        clean_results = [r for r in results if r is not None]
        
        print(f"\n--- Finished! Analyzed {len(clean_results)} strategies. ---")
        return pd.DataFrame(clean_results)