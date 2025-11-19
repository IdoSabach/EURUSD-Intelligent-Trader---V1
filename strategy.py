from indicators import Indicators
import numpy as np

class Strategy(Indicators):
  def __init__(self,df):
    super().__init__(df)


  def position(self, mean_ATR2 = 50, range_ATR = 0.6):
    df = self.data
    # Default
    df['position'] = 0
    df.loc[df['sessions'] == 'deadzone', 'position'] = 0    

    df[f"ATR_{mean_ATR2}"] = df['ATR_14'].rolling(mean_ATR2).mean()
    # df.dropna(inplace=True)

    normal_vol = ((df['ATR_14'] >= range_ATR * df['ATR_50']) & 
                  (df['ATR_14'] <= (range_ATR*3) * df['ATR_50']))
    
    # Trend
    
    long_trend = ((df['price'] > df['SMA_200']) & 
                  (df['SMA_100'] > df['SMA_200']) & 
                  (df['SMA_20'] > df['SMA_100']))
    
    short_trend = ((df['price'] < df['SMA_200']) & 
                   (df['SMA_100'] < df['SMA_200']) & 
                   (df['SMA_20'] < df['SMA_100']))
    # Trigger
    long_trigger = df['price'] <= df['BB_lower']
    short_trigger = df['price'] >= df['BB_upper']
    
    df.loc[long_trend & long_trigger & normal_vol, 'position'] = 1
    df.loc[short_trend & short_trigger & normal_vol, 'position'] = -1

  def build_trade_state(self):
    df = self.data

    df['long_entry'] = np.where(df['position'] == 1, 1, 0)
    df['short_entry'] = np.where(df['position'] == -1, 1, 0)

    df['long_group'] = (df['long_entry'] == 1).cumsum()
    df['short_group'] = (df['short_entry'] == 1).cumsum()

    df['long_entry_price'] = df.groupby('long_group')['price'].transform('first')
    df['long_entry_atr'] = df.groupby('long_group')['ATR_14'].transform('first')

    df['short_entry_price'] = df.groupby('short_group')['price'].transform('first')
    df['short_entry_atr'] = df.groupby('short_group')['ATR_14'].transform('first')

    # Long exit
    df['long_sl'] = df['price'] <= df['long_entry_price'] - df['long_entry_atr'] * 1.3
    df['long_tp'] = df['price'] >= df['long_entry_price'] + df['long_entry_atr'] * 2
    df['long_exit'] = df['long_sl'] | df['long_tp']
    df['long_exit_cum'] = df.groupby('long_group')['long_exit'].cumsum()
    df['long_active'] = (df['long_group'] > 0) & (df['long_exit_cum'] == 0)

    # Short exit
    df['short_sl'] = df['price'] >= df['short_entry_price'] + df['short_entry_atr'] * 1.3
    df['short_tp'] = df['price'] <= df['short_entry_price'] - df['short_entry_atr'] * 2
    df['short_exit'] = df['short_sl'] | df['short_tp']
    df['short_exit_cum'] = df.groupby('short_group')['short_exit'].cumsum()
    df['short_active'] = (df['short_group'] > 0) & (df['short_exit_cum'] == 0)

    df['trade_state'] = 0
    df.loc[df['long_active'], 'trade_state'] = 1
    df.loc[df['short_active'], 'trade_state'] = -1

    df.drop(columns=['long_group', 'short_group', 'long_entry_price', 'long_entry_atr', 'short_entry_price',
                     'short_entry_atr', 'long_sl', 'long_tp', 'long_exit', 'long_exit_cum', 'long_active', 'short_sl',
                      'short_tp', 'short_exit', 'short_exit_cum', 'short_active'], inplace=True)


  def run(self):
    self.process_data()
    super().run()
    self.position()
    self.build_trade_state()
    self.data.dropna(inplace=True)




  # for i in range(len(df)):
    #   if (df['long_entry'].iloc[i] == 1) or long_trade:
    #     long_trade = True
    #     entry_price = df['price'].iloc[i]
    #     atr_entry = df['ATR_14'].iloc[i] 
    #     df['trade_state'].iloc[i] = 1
    #     if(df['price'].iloc[i] <= entry_price - (atr_entry*1.3)) or (df['price'].iloc[i] >= entry_price + (atr_entry*2)):
    #       df['trade_state'].iloc[i] = 1
    #       long_trade = False
    #   elif (df['short_entry'].iloc[i] == 1) or short_trade:
    #     short_trade = True
    #     entry_price = df['price'].iloc[i]
    #     atr_entry = df['ATR_14'].iloc[i] 
    #     df['trade_state'].iloc[i] = -1
    #     if(df['price'].iloc[i] >= entry_price + (atr_entry*1.3)) or (df['price'].iloc[i] <= entry_price - (atr_entry*2)):
    #       df['trade_state'].iloc[i] = -1
    #       short_trade = False
    #   else:
    #     df['trade_state'].iloc[i] = 0




      # def build_trade_state(self):
  #   df = self.data

  #   df['long_entry'] = np.where(df['position']==1, 1,0).astype(int)
  #   df['short_entry'] = np.where(df['position']==-1, 1,0).astype(int)

  #   df['entry_price'] = df['price'].where(df['position'] != 0).ffill()
  #   df['entry_ATR'] = df['ATR_14'].where(df['position'] != 0).ffill()

  #   exit_long_trendWeak = df['price'] < df['SMA_20']
  #   exit_long_lowVol = df['ATR_14'] < 0.6 * df['ATR_50']
  #   SL_long = df['Low'].shift(1) - 1.3 * df['ATR_14']
  #   exit_long_SL = df['price'] <= SL_long
  #   TP_long = df['entry_price']+ 2.5 * df['entry_ATR']
  #   exit_long_TP = df['price'] >= TP_long
  #   exit_long = exit_long_trendWeak | exit_long_lowVol | exit_long_SL | exit_long_TP

  #   exit_short_trendWeak = df['price'] > df['SMA_20']
  #   exit_short_lowVol = df['ATR_14'] < 0.6 * df['ATR_50']
  #   SL_short = df['Low'].shift(1) + 1.3 * df['ATR_14']
  #   exit_short_SL = df['price'] >= SL_short
  #   TP_short = df['entry_price']- 2.5 * df['entry_ATR']
  #   exit_short_TP = df['price'] <= TP_short
  #   exit_short = exit_short_trendWeak | exit_short_lowVol | exit_short_SL | exit_short_TP

  #   df['long_exit'] = np.where(exit_long, 1,0).astype(int)
  #   df['short_exit'] = np.where(exit_short, 1,0).astype(int)


  #   trade_state = []
  #   current_pos = 0  

  #   for i in range(len(df)):

  #       if df['long_entry'].iloc[i] == 1 and current_pos == 0:
  #           current_pos = 1
  #       elif df['short_entry'].iloc[i] == 1 and current_pos == 0:
  #           current_pos = -1

  #       if df['long_exit'].iloc[i] == 1 and current_pos == 1:
  #           current_pos = 0

  #       if df['short_exit'].iloc[i] == 1 and current_pos == -1:
  #           current_pos = 0

  #       trade_state.append(current_pos)

  #   df['trade_state'] = trade_state

  #   df["clean_long_entry"] = np.where((df["trade_state"].shift(1) == 0) & (df["trade_state"] == 1),1, 0)
  #   df["clean_short_entry"] = np.where((df["trade_state"].shift(1) == 0) & (df["trade_state"] == -1),1, 0)

  #   df["clean_long_exit"] = np.where((df["trade_state"].shift(1) == 1) & (df["trade_state"] == 0),1, 0)
  #   df["clean_short_exit"] = np.where((df["trade_state"].shift(1) == -1) & (df["trade_state"] == 0),1, 0)
