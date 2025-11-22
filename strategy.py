import numpy as np
import pandas as pd
from indicators import Indicators

class Strategy(Indicators):
    """
    Implements the trading logic: Trend + Hook + Volatility.
    Includes INT conversion fix to prevent 'SMA_200.0' errors.
    """
    def __init__(self, df, params=None):
        super().__init__(df)
        
        self.default_params = {
            'sma_fast': 15,
            'sma_slow': 100,
            'sma_trend': 200,
            'bb_period': 20,
            'bb_std': 2.0,
            'atr_period': 14,
            'range_atr_filter': 0.8,
            'sl_multiplier': 2.0,
            'tp_multiplier': 5.0,
            'be_multiplier': 100.0
        }
        
        self.params = self.default_params.copy()
        if params:
            self.params.update(params)

    def run_strategy(self):
        self.calculate_all(self.params)
        self._generate_signals()
        self._calculate_exit_levels()

    def _generate_signals(self):
        df = self.data
        p = self.params
        
        # --- התיקון: המרה למספר שלם (int) כדי למנוע .0 בשם העמודה ---
        sma_fast = f"SMA_{int(p['sma_fast'])}"
        sma_slow = f"SMA_{int(p['sma_slow'])}"
        sma_trend = f"SMA_{int(p['sma_trend'])}"
        atr_col = f"ATR_{int(p['atr_period'])}"
        # -----------------------------------------------------------
        
        # 1. Trend Filter
        long_trend = (df['price'] > df[sma_trend]) & (df[sma_fast] > df[sma_slow])
        short_trend = (df['price'] < df[sma_trend]) & (df[sma_fast] < df[sma_slow])
        
        # 2. Bollinger Hook
        long_hook = (df['price'].shift(1) <= df['BB_lower'].shift(1)) & (df['price'] > df['BB_lower'])
        short_hook = (df['price'].shift(1) >= df['BB_upper'].shift(1)) & (df['price'] < df['BB_upper'])
        
        # 3. Volatility Filter
        df['ATR_50'] = df[atr_col].rolling(50).mean()
        volatility_ok = df[atr_col] >= (p['range_atr_filter'] * df['ATR_50'])

        df['position'] = 0
        df.loc[long_trend & long_hook & volatility_ok, 'position'] = 1
        df.loc[short_trend & short_hook & volatility_ok, 'position'] = -1
        
        if 'session' in df.columns:
            df.loc[df['session'] == 'deadzone', 'position'] = 0

    def _calculate_exit_levels(self):
        df = self.data
        # גם כאן: המרה ל-int
        atr_col = f"ATR_{int(self.params['atr_period'])}"
        
        atr = df[atr_col]
        sl_mult = self.params['sl_multiplier']
        tp_mult = self.params['tp_multiplier']
        
        df['long_sl_val'] = df['price'] - (atr * sl_mult)
        df['long_tp_val'] = df['price'] + (atr * tp_mult)
        
        df['short_sl_val'] = df['price'] + (atr * sl_mult)
        df['short_tp_val'] = df['price'] - (atr * tp_mult)