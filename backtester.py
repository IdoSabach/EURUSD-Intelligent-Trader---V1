import numpy as np
import pandas as pd
from strategy import Strategy

class Backtester(Strategy):

    def __init__(self, df, position_size=10):
        """
        :param df: DataFrame with OHLCV data
        :param position_size: Number of units per trade (default 10)
        """
        super().__init__(df)
        self.position_size = position_size
        self.metrics = {}
        self.trade_log = None # יחזיק את טבלת הטריידים המסוכמת

    def compute_equity_curve(self):
        """מחשב את עקומת ההון של אסטרטגיית קנה-החזק מול האלגוריתם"""
        df = self.data.copy()

        # הסטת הפוזיציה ביום אחד קדימה (כדי למנוע Lookahead Bias)
        df['position'] = df['trade_state'].shift(1).fillna(0)
        
        # חישוב תשואת האסטרטגיה
        df['strategy'] = df['position'] * df['returns']

        # חישוב תשואה מצטברת (Equity Curve)
        df['creturns'] = df['returns'].cumsum().apply(np.exp)   # Buy & Hold
        df['cstrategy'] = df['strategy'].cumsum().apply(np.exp) # Strategy

        self.data = df

    def generate_trade_log(self):
        """מייצר טבלה שבה כל שורה היא טרייד בודד עם מחיר כניסה, יציאה ורווח"""
        # עובדים על עותק כדי לא לשנות את המקור
        df = self.data.copy()

        # === התיקון כאן ===
        # אם Datetime הוא האינדקס, נהפוך אותו לעמודה רגילה כדי שנוכל להשתמש בו ב-agg
        if 'Datetime' not in df.columns:
            df = df.reset_index()
            # מוודאים שהעמודה החדשה אכן נקראת Datetime (לפעמים זה נקרא 'index')
            if 'Datetime' not in df.columns and 'index' in df.columns:
                 df = df.rename(columns={'index': 'Datetime'})
        # ==================

        # 1. יצירת מזהה ייחודי לכל טרייד (Trade ID)
        df['long_group'] = (df['long_entry'] == 1).cumsum()
        df['short_group'] = (df['short_entry'] == 1).cumsum()
        df['trade_id'] = df['long_group'] + df['short_group']
        
        # זיהוי סוג הטרייד
        df['trade_type'] = np.where(df['long_entry'] == 1, 'Long', 
                                    np.where(df['short_entry'] == 1, 'Short', None))

        # סינון רק לשורות ששיכות לטרייד פעיל
        active_trades = df[df['trade_id'] > 0].copy()
        
        if active_trades.empty:
            self.trade_log = pd.DataFrame()
            return self.trade_log

        # 2. קיבוץ לפי Trade ID
        grouped = active_trades.groupby('trade_id')

        # 3. חילוץ נתוני הטרייד (Aggregation)
        # כעת Datetime הוא עמודה רגילה והשגיאה תיעלם
        trade_log = grouped.agg(
            trade_type=('trade_type', 'first'),
            entry_time=('Datetime', 'first'),
            exit_time=('Datetime', 'last'),
            entry_price=('price', 'first'),
            exit_price=('price', 'last')
        ).reset_index()

        # 4. חישובי זמנים
        trade_log['entry_time'] = pd.to_datetime(trade_log['entry_time'])
        trade_log['exit_time'] = pd.to_datetime(trade_log['exit_time'])
        trade_log['duration'] = trade_log['exit_time'] - trade_log['entry_time']
        trade_log['duration_mins'] = trade_log['duration'].dt.total_seconds() / 60

        # 5. חישוב P&L (רווח והפסד)
        trade_log['pnl_percent'] = np.where(
            trade_log['trade_type'] == 'Long',
            (trade_log['exit_price'] - trade_log['entry_price']) / trade_log['entry_price'],
            (trade_log['entry_price'] - trade_log['exit_price']) / trade_log['entry_price']
        ) * 100

        trade_log['pnl_usd'] = np.where(
            trade_log['trade_type'] == 'Long',
            (trade_log['exit_price'] - trade_log['entry_price']) * self.position_size,
            (trade_log['entry_price'] - trade_log['exit_price']) * self.position_size
        )

        # סינון טריידים לא תקינים (משך 0)
        trade_log = trade_log[trade_log['duration_mins'] > 0].copy()
        
        self.trade_log = trade_log
        return self.trade_log

    def calculate_metrics(self):
        """מחשב את מדדי הביצועים המורחבים (כולל Calmar, SQN, Recovery Factor ועוד)"""
        df = self.data
        trades = self.trade_log

        if trades is None or trades.empty:
            return {"Error": "No trades executed"}

        # --- 1. נתונים בסיסיים לחישוב ---
        total_trades = len(trades)
        winning_trades = trades[trades['pnl_usd'] > 0]
        losing_trades = trades[trades['pnl_usd'] <= 0]

        # --- 2. מדדי הצלחה בסיסיים ---
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = winning_trades['pnl_usd'].mean() if not winning_trades.empty else 0
        avg_loss = losing_trades['pnl_usd'].mean() if not losing_trades.empty else 0
        
        gross_profit = winning_trades['pnl_usd'].sum()
        gross_loss = abs(losing_trades['pnl_usd'].sum())
        net_profit = gross_profit - gross_loss

        profit_factor = (gross_profit / gross_loss) if gross_loss != 0 else np.inf

        expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * abs(avg_loss))

        # --- 3. מדדי תיק וסיכון (Portfolio & Risk) ---
        cumulative_returns = df['cstrategy']
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        
        # Max Drawdown באחוזים
        max_drawdown_pct = drawdown.min() * 100 
        
        # Total Return באחוזים
        total_return_pct = (cumulative_returns.iloc[-1] - 1) * 100
        buy_hold_return_pct = (df['creturns'].iloc[-1] - 1) * 100

        # --- 4. מדדים מתקדמים (החדשים!) ---
        
        # א. חישוב רצף הפסדים מקסימלי (Max Consecutive Losses)
        # יוצרים סדרה בוליאנית: אמת אם הפסד, שקר אם רווח
        is_loss = trades['pnl_usd'] < 0
        # מקבצים רצפים זהים ומסכמים אותם
        consecutive_losses = is_loss.groupby((is_loss != is_loss.shift()).cumsum()).cumsum()
        # לוקחים את המקסימום מתוך הרצפים שהם באמת הפסדים
        max_consecutive_losses = consecutive_losses[is_loss].max() if not losing_trades.empty else 0

        # ב. Recovery Factor (פקטור התאוששות)
        # Net Profit / Max Drawdown USD (או ביחס לתשואה)
        # כאן נשתמש ביחס התשואה לאחוז ה-DD
        recovery_factor = (total_return_pct / abs(max_drawdown_pct)) if max_drawdown_pct != 0 else np.inf

        # ג. SQN (System Quality Number)
        # SQN = SquareRoot(N) * (Avg Profit / Std Dev Profit)
        pnl_std = trades['pnl_usd'].std()
        avg_pnl = trades['pnl_usd'].mean()
        if pnl_std != 0 and total_trades > 0:
            sqn = np.sqrt(total_trades) * (avg_pnl / pnl_std)
        else:
            sqn = 0

        # ד. חישוב Calmar Ratio (דורש תשואה שנתית)
        # נחשב כמה שנים יש בדאטה
        try:
            start_date = df.index[0]
            end_date = df.index[-1]
            duration_days = (end_date - start_date).days
            years = duration_days / 365.25
            
            if years > 0 and max_drawdown_pct != 0:
                # CAGR (Compound Annual Growth Rate)
                cagr = ((cumulative_returns.iloc[-1]) ** (1 / years)) - 1
                calmar_ratio = cagr / abs(max_drawdown_pct / 100) # יחס בין תשואה שנתית ל-DD
            else:
                calmar_ratio = 0
        except Exception:
            calmar_ratio = 0

        # ה. Average Duration (משך זמן ממוצע)
        avg_duration = trades['duration'].mean()

        # ו. Sharpe Ratio
        try:
            # המרה לאינדקס תאריך לצורך Resample
            temp_df = df.copy()
            if 'Datetime' in temp_df.columns and not isinstance(temp_df.index, pd.DatetimeIndex):
                temp_df = temp_df.set_index('Datetime')
            
            daily_returns = temp_df['cstrategy'].resample('D').last().pct_change().dropna()
            if daily_returns.std() != 0:
                sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
            else:
                sharpe_ratio = 0
        except Exception:
            sharpe_ratio = 0

        # --- 5. שמירת התוצאות ---
        self.metrics = {
            'Total Trades': int(total_trades),
            'Win Rate (%)': round(win_rate, 2),

            'Avg Win ($)': round(avg_win, 2),
            'Avg Loss ($)': round(avg_loss, 2),
            'Profit Factor': round(profit_factor, 2),

            'Max Drawdown (%)': round(max_drawdown_pct, 2),
            'Max Consec. Losses': int(max_consecutive_losses),

            'Expectancy ($)': round(expectancy, 2),
            'SQN Score': round(sqn, 2),

            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Calmar Ratio': round(calmar_ratio, 2),
                                    
            'Avg Duration': str(avg_duration).split('.')[0], 
            'Recovery Factor': round(recovery_factor, 2),
            'Total Return (%)': round(total_return_pct, 2),
            'Buy & Hold (%)': round(buy_hold_return_pct, 2)
        }
        
        return self.metrics

    def run_backtest(self):
        """מריץ את כל התהליך ומחזיר את המדדים"""
        super().run()                # 1. הרצת האסטרטגיה (Indicators + Signals)
        self.compute_equity_curve()  # 2. חישוב תשואות מצטברות
        self.generate_trade_log()    # 3. יצירת יומן עסקאות
        self.calculate_metrics()     # 4. חישוב מדדים סופיים
        return self.metrics

    def print_summary(self):
        """מדפיס את הדוח בצורה יפה"""
        print("\n==== Hedge Fund Performance Report ====")
        for k, v in self.metrics.items():
            print(f"{k:<20}: {v}")