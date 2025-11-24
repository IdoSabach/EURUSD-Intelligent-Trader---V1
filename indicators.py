import pandas as pd
import numpy as np

class Indicators:
    def __init__(self, df):
        self.data = df.copy()

    def calculate_all(self, params):
        df = self.data
        
        p_fast = int(params['sma_fast'])
        p_slow = int(params['sma_slow'])
        p_trend = int(params['sma_trend'])
        p_bb = int(params['bb_period'])
        p_atr = int(params['atr_period'])
        
        # 1. SMA
        df[f"SMA_{p_fast}"] = df['price'].rolling(p_fast).mean()
        df[f"SMA_{p_slow}"] = df['price'].rolling(p_slow).mean()
        df[f"SMA_{p_trend}"] = df['price'].rolling(p_trend).mean()
        
        # 2. Bollinger Bands
        bb_std = params['bb_std']
        ma = df['price'].rolling(p_bb).mean()
        sigma = df['price'].rolling(p_bb).std()
        
        df['BB_upper'] = ma + (bb_std * sigma)
        df['BB_lower'] = ma - (bb_std * sigma)
        
        # 3. ATR
        high = df['High']
        low = df['Low']
        close = df['price'].shift(1)
        
        tr1 = high - low
        tr2 = np.abs(high - close)
        tr3 = np.abs(low - close)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        df[f"ATR_{p_atr}"] = tr.rolling(p_atr).mean()
        df['ATR_50'] = tr.rolling(50).mean()
        
        self.data = df.dropna()