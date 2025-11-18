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

    df['long_entry'] = np.where(df['position']==1, 1,0).astype(int)
    df['short_entry'] = np.where(df['position']==-1, 1,0).astype(int)

    target_hit_long = df['price'] >= df['BB_mid']
    target_hit_short = df['price'] <= df['BB_mid']
    sl_tp_hit = 0

    df['long_exit'] = np.where(target_hit_long | (sl_tp_hit == 1), 1,0)
    df['short_exit'] = np.where(target_hit_short | (sl_tp_hit == 1), 1,0)


  def build_trade_state(self):
    df = self.data

    trade_state = []
    current_pos = 0  

    for i in range(len(df)):

        # כניסה ללונג
        if df['long_entry'].iloc[i] == 1 and current_pos == 0:
            current_pos = 1
        
        # כניסה לשורט
        elif df['short_entry'].iloc[i] == 1 and current_pos == 0:
            current_pos = -1

        # יציאה מלונג
        if df['long_exit'].iloc[i] == 1 and current_pos == 1:
            current_pos = 0

        # יציאה משורט
        if df['short_exit'].iloc[i] == 1 and current_pos == -1:
            current_pos = 0

        # הוספת מצב העסקה
        trade_state.append(current_pos)

    df['trade_state'] = trade_state



  def run(self):
    super().run()
    self.position()
    self.build_trade_state()



    # exit_long_trendWeak = df['price'] < df['SMA_20']
    # exit_long_lowVol = df['ATR_14'] < 0.6 * df['ATR_50']
    # SL_long = df['Low'].shift(1) - 1.3 * df['ATR_14']
    # exit_long_SL = df['price'] <= SL_long
    # TP_long = entry_price + 2.5 * entry_ATR
    # exit_long_TP = df['price'] >= TP_long
    # exit_long = exit_long_trendWeak | exit_long_lowVol | exit_long_SL | exit_long_TP

    # exit_short_trendWeak = df['price'] > df['SMA_20']
    # exit_short_lowVol = df['ATR_14'] < 0.6 * df['ATR_50']
    # SL_short = df['Low'].shift(1) + 1.3 * df['ATR_14']
    # exit_short_SL = df['price'] >= SL_short
    # TP_short = entry_price - 2.5 * entry_ATR
    # exit_short_TP = df['price'] <= TP_short
    # exit_short = exit_short_trendWeak | exit_short_lowVol | exit_short_SL | exit_short_TP

    # df['long_exit'] = np.where(exit_long, 1,0)
    # df['short_exit'] = np.where(exit_short, 1,0)







    