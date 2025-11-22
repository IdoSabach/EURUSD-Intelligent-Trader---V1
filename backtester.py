import numpy as np
import pandas as pd
from strategy import Strategy

class Backtester(Strategy):
    """
    Executes the backtest simulation using a high-performance Numpy engine.
    Handles trade execution, P&L calculation, and performance metrics.
    """
    def __init__(self, df, params=None, position_size=10):
        super().__init__(df, params)
        self.position_size = position_size
        self.metrics = {}
        self.trade_log = pd.DataFrame()

    def run_backtest(self):
        """
        Full workflow: Strategy -> Simulation -> Metrics
        """
        self.run_strategy()
        self._generate_trade_log_numpy()
        return self.calculate_metrics()

    def _generate_trade_log_numpy(self):
        """
        Optimized simulation engine using Numpy arrays for speed.
        Iterates through entry signals and scans future prices for exit conditions.
        """
        df = self.data.copy()
        
        # Ensure Datetime is accessible
        if 'Datetime' not in df.columns:
            df = df.reset_index()
            if 'Datetime' not in df.columns and 'index' in df.columns:
                 df = df.rename(columns={'index': 'Datetime'})

        # Convert DataFrame columns to Numpy arrays (Speed boost!)
        prices = df['price'].values
        highs = df['High'].values
        lows = df['Low'].values
        datetimes = df['Datetime'].values
        positions = df['position'].values
        
        # Pre-calculated Exit Levels from Strategy
        long_sl = df['long_sl_val'].values
        long_tp = df['long_tp_val'].values
        short_sl = df['short_sl_val'].values
        short_tp = df['short_tp_val'].values

        trades_list = []
        
        # Find indices where a trade starts
        entry_indices = np.where(positions != 0)[0]

        for idx in entry_indices:
            # Stop if not enough data points left
            if idx >= len(prices) - 1: continue
            
            entry_type = positions[idx] # 1 (Long) or -1 (Short)
            entry_price = prices[idx]
            entry_time = datetimes[idx]
            
            # Get targets for this specific trade
            if entry_type == 1:
                sl = long_sl[idx]
                tp = long_tp[idx]
            else:
                sl = short_sl[idx]
                tp = short_tp[idx]
            
            exit_idx = -1
            exit_price = entry_price
            
            # Slice arrays for future candles
            search_highs = highs[idx+1:]
            search_lows = lows[idx+1:]
            
            # --- Fast Inner Loop: Scan for Exit ---
            for i in range(len(search_highs)):
                current_high = search_highs[i]
                current_low = search_lows[i]
                
                if entry_type == 1: # Long Logic
                    if current_low <= sl:   # Stop Loss Hit
                        exit_price = sl
                        exit_idx = idx + 1 + i
                        break
                    if current_high >= tp:   # Take Profit Hit
                        exit_price = tp
                        exit_idx = idx + 1 + i
                        break
                
                else: # Short Logic
                    if current_high >= sl:   # Stop Loss Hit
                        exit_price = sl
                        exit_idx = idx + 1 + i
                        break
                    if current_low <= tp:   # Take Profit Hit
                        exit_price = tp
                        exit_idx = idx + 1 + i
                        break
            
            # Record trade if exited
            if exit_idx != -1:
                exit_time = datetimes[exit_idx]
                ts_entry = pd.Timestamp(entry_time)
                ts_exit = pd.Timestamp(exit_time)
                duration = ts_exit - ts_entry
                
                if entry_type == 1:
                    pnl_usd = (exit_price - entry_price) * self.position_size
                else:
                    pnl_usd = (entry_price - exit_price) * self.position_size
                
                trades_list.append({
                    'entry_time': ts_entry,
                    'exit_time': ts_exit,
                    'trade_type': 'Long' if entry_type == 1 else 'Short',
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl_usd': pnl_usd,
                    'duration': duration,
                    'duration_mins': duration.total_seconds() / 60
                })

        self.trade_log = pd.DataFrame(trades_list)
        return self.trade_log

    def calculate_metrics(self):
        """Calculates KPI metrics for the strategy."""
        trades = self.trade_log
        
        if trades.empty: 
            return {
                'Total Trades': 0, 'Total Profit ($)': 0, 'Profit Factor': 0, 
                'Max Drawdown ($)': 0, 'Win Rate (%)': 0, 'Max Consec. Losses': 0
            }
        
        total_trades = len(trades)
        gross_profit = trades[trades['pnl_usd'] > 0]['pnl_usd'].sum()
        gross_loss = abs(trades[trades['pnl_usd'] <= 0]['pnl_usd'].sum())
        
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.inf
        total_profit = trades['pnl_usd'].sum()
        win_rate = (len(trades[trades['pnl_usd']>0]) / total_trades) * 100
        
        # Drawdown Calculation
        trades = trades.sort_values('exit_time')
        equity = trades['pnl_usd'].cumsum()
        dd = (equity - equity.cummax()).min()

        # Consecutive Losses Calculation
        is_loss = trades['pnl_usd'] <= 0
        if is_loss.any():
            groups = (is_loss != is_loss.shift()).cumsum()
            consecutive_losses = is_loss.groupby(groups).cumsum()
            max_consec_losses = consecutive_losses[is_loss].max()
            if pd.isna(max_consec_losses): max_consec_losses = 0
        else:
            max_consec_losses = 0
        
        self.metrics = {
            'Total Trades': int(total_trades),
            'Profit Factor': round(profit_factor, 2),
            'Win Rate (%)': round(win_rate, 2),
            'Total Profit ($)': round(total_profit, 2),
            'Max Drawdown ($)': round(dd, 2),
            'Max Consec. Losses': int(max_consec_losses)
        }
        return self.metrics
        
    def print_summary(self):
        print("\n==== Strategy Performance Report ====")
        for k, v in self.metrics.items():
            print(f"{k:<20}: {v}")