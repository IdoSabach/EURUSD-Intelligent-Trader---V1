from indicators import Indicators
import numpy as np

class Strategy(Indicators):
  def __init__(self,df):
    super().__init__(df)
    self.run()


  def position(self):
    df = self.data
    # Default
    df['position'] = 0
    # Remove Deadzone
    df.loc[df['sessions'] == 'deadzone', 'position'] = 0    
    # Calculate vol
    df['ATR_50'] = df['ATR_14'].rolling(50).mean()
    # df.dropna(inplace=True)

    low_vol = df['ATR_14'] < 0.8 * df['ATR_50']
    normal_vol = ((df['ATR_14'] >= 0.8 * df['ATR_50']) & 
                  (df['ATR_14'] <= 1.6 * df['ATR_50']))
    
    high_vol = df['ATR_14'] > 1.6 * df['ATR_50']
    # Trend
    long_trend = ((df['price'] > df['SMA_200']) & 
                  (df['SMA_100'] > df['SMA_200']) & 
                  (df['SMA_20'] > df['SMA_100']))
    
    short_trend = ((df['price'] < df['SMA_200']) & 
                   (df['SMA_100'] < df['SMA_200']) & 
                   (df['SMA_20'] < df['SMA_100']))
    # Trigger
    long_trigger = df['price'] < df['BB_lower']
    short_trigger = df['price'] > df['BB_upper']
    # Entry only vol valid
    valid_vol = normal_vol
    # Entry
    df.loc[long_trend & long_trigger & valid_vol, 'position'] = 1
    df.loc[short_trend & short_trigger & valid_vol, 'position'] = -1

  def run(self):
    super().run()
    self.position()
