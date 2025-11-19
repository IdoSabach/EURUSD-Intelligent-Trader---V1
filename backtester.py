import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from strategy import Strategy

class Backtester(Strategy):

    def __init__(self, df):
        super().__init__(df)
        self.metrics = {}

    def compute_returns(self):
        df = self.data.copy()

        df['position'] = df['trade_state'].shift(1).fillna(0)
        df['strategy'] = df['position'] * df['returns']

        # Buy & Hold
        df['creturns'] = df['returns'].cumsum().apply(np.exp)

        # אסטרטגיה
        df['cstrategy'] = df['strategy'].cumsum().apply(np.exp)

        self.data = df

    def run_backtest(self):
        super().run()
        self.compute_returns()

        final_buy_hold = self.data['creturns'].iloc[-1] - 1
        final_strategy = self.data['cstrategy'].iloc[-1] - 1

        self.metrics = {
            'buy_and_hold_return': final_buy_hold,
            'strategy_return': final_strategy
        }

        return self.metrics

    def summary(self):
        print("==== Simple Backtest Summary ====")
        print(f"Buy & Hold Return:  {self.metrics['buy_and_hold_return']:.2%}")
        print(f"Strategy Return:    {self.metrics['strategy_return']:.2%}")
