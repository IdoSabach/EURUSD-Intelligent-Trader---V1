import numpy as np
import pandas as pd
from strategy import Strategy

class Backtester(Strategy):
    def __init__(self, df, params=None, position_size=1000):
        super().__init__(df, params)
        self.position_size = position_size
        self.metrics = {}
        self.trade_log = pd.DataFrame()

    def run_backtest(self):
        self.run_strategy()
        self.generate_trade_log()
        return self.calculate_metrics()

    def generate_trade_log(self):
        df = self.data.copy()
        if 'Datetime' not in df.columns:
            df = df.reset_index()
            if 'Datetime' not in df.columns and 'index' in df.columns:
                 df = df.rename(columns={'index': 'Datetime'})

        prices = df['price'].values
        highs = df['High'].values
        lows = df['Low'].values
        datetimes = df['Datetime'].values
        positions = df['position'].values
        
        atr_col = f"ATR_{self.params['atr_period']}"
        atrs = df[atr_col].values

        sl_mult = self.params['sl_multiplier']
        tp_mult = self.params['tp_multiplier']
        be_mult = self.params.get('be_multiplier', 100)

        trades_list = []
        entry_indices = np.where(positions != 0)[0]

        for idx in entry_indices:
            if idx >= len(prices) - 1: continue
            
            entry_type = positions[idx]
            entry_price = prices[idx]
            atr = atrs[idx]
            entry_time = datetimes[idx]
            
            if entry_type == 1: # Long
                sl = entry_price - (atr * sl_mult)
                tp = entry_price + (atr * tp_mult)
                be_trigger = entry_price + (atr * be_mult)
            else: # Short
                sl = entry_price + (atr * sl_mult)
                tp = entry_price - (atr * tp_mult)
                be_trigger = entry_price - (atr * be_mult)
            
            is_be_active = False
            exit_idx = -1
            exit_price = entry_price # Default
            
            search_highs = highs[idx+1:]
            search_lows = lows[idx+1:]
            
            for i in range(len(search_highs)):
                current_high = search_highs[i]
                current_low = search_lows[i]
                
                if entry_type == 1: # Long
                    if current_low <= sl:   # SL
                        exit_price = sl; exit_idx = idx + 1 + i; break
                    if current_high >= tp:   # TP
                        exit_price = tp; exit_idx = idx + 1 + i; break
                    if not is_be_active and current_high >= be_trigger:
                        sl = entry_price; is_be_active = True
                else: # Short
                    if current_high >= sl:   # SL
                        exit_price = sl; exit_idx = idx + 1 + i; break
                    if current_low <= tp:   # TP
                        exit_price = tp; exit_idx = idx + 1 + i; break
                    if not is_be_active and current_low <= be_trigger:
                        sl = entry_price; is_be_active = True
            
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
                    'duration': duration
                })

        self.trade_log = pd.DataFrame(trades_list)
        return self.trade_log

    def calculate_metrics(self):
        """
        חישוב מורחב של מדדים כולל משך זמן, ממוצעים ורצפים.
        """
        trades = self.trade_log
        if trades.empty:
            return {'Total Trades': 0, 'Total Profit ($)': 0, 'Profit Factor': 0, 'Max Drawdown ($)': 0}
        
        total_trades = len(trades)
        wins = trades[trades['pnl_usd'] > 0]
        losses = trades[trades['pnl_usd'] <= 0]
        
        gross_win = wins['pnl_usd'].sum()
        gross_loss = abs(losses['pnl_usd'].sum())
        total_profit = trades['pnl_usd'].sum()
        
        profit_factor = gross_win / gross_loss if gross_loss > 0 else 999
        win_rate = (len(wins) / total_trades) * 100
        
        avg_win = wins['pnl_usd'].mean() if not wins.empty else 0
        avg_loss = losses['pnl_usd'].mean() if not losses.empty else 0
        risk_reward_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        best_trade = trades['pnl_usd'].max()
        worst_trade = trades['pnl_usd'].min()
        
        avg_duration = trades['duration'].mean()
        
        trades = trades.sort_values('exit_time')
        equity = trades['pnl_usd'].cumsum()
        dd = (equity - equity.cummax()).min()

        is_loss = trades['pnl_usd'] <= 0
        cons_losses = 0
        if is_loss.any():
            cons_losses = is_loss.groupby((is_loss != is_loss.shift()).cumsum()).cumsum()[is_loss].max()
            
        is_win = trades['pnl_usd'] > 0
        cons_wins = 0
        if is_win.any():
            cons_wins = is_win.groupby((is_win != is_win.shift()).cumsum()).cumsum()[is_win].max()

        self.metrics = {
            'Total Trades': int(total_trades),
            'Total Profit ($)': round(total_profit, 2),
            'Profit Factor': round(profit_factor, 2),
            'Win Rate (%)': round(win_rate, 2),
            'Max Drawdown ($)': round(dd, 2),
            'Avg Win ($)': round(avg_win, 2),
            'Avg Loss ($)': round(avg_loss, 2),
            'Risk/Reward Ratio': round(risk_reward_ratio, 2),
            'Best Trade ($)': round(best_trade, 2),
            'Worst Trade ($)': round(worst_trade, 2),
            'Max Consec. Wins': int(cons_wins),
            'Max Consec. Losses': int(cons_losses),
            'Avg Duration': str(avg_duration).split('.')[0]
        }
        return self.metrics
    
    def print_summary(self):
        print("\n" + "="*40)
        print("📊 FULL STRATEGY REPORT")
        print("="*40)
        for k, v in self.metrics.items():
            print(f"{k:<25}: {v}")
        print("="*40 + "\n")