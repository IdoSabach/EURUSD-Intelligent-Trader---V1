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

    


  def build_trade_state(self):
    df = self.data

    df['long_entry'] = np.where(df['position']==1, 1,0).astype(int)
    df['short_entry'] = np.where(df['position']==-1, 1,0).astype(int)

    df['entry_price'] = df['price'].where(df['position'] != 0).ffill()
    df['entry_ATR'] = df['ATR_14'].where(df['position'] != 0).ffill()

    exit_long_trendWeak = df['price'] < df['SMA_20']
    exit_long_lowVol = df['ATR_14'] < 0.6 * df['ATR_50']
    SL_long = df['Low'].shift(1) - 1.3 * df['ATR_14']
    exit_long_SL = df['price'] <= SL_long
    TP_long = df['entry_price']+ 2.5 * df['entry_ATR']
    exit_long_TP = df['price'] >= TP_long
    exit_long = exit_long_trendWeak | exit_long_lowVol | exit_long_SL | exit_long_TP

    exit_short_trendWeak = df['price'] > df['SMA_20']
    exit_short_lowVol = df['ATR_14'] < 0.6 * df['ATR_50']
    SL_short = df['Low'].shift(1) + 1.3 * df['ATR_14']
    exit_short_SL = df['price'] >= SL_short
    TP_short = df['entry_price']- 2.5 * df['entry_ATR']
    exit_short_TP = df['price'] <= TP_short
    exit_short = exit_short_trendWeak | exit_short_lowVol | exit_short_SL | exit_short_TP

    df['long_exit'] = np.where(exit_long, 1,0).astype(int)
    df['short_exit'] = np.where(exit_short, 1,0).astype(int)


    trade_state = []
    current_pos = 0  

    for i in range(len(df)):

        if df['long_entry'].iloc[i] == 1 and current_pos == 0:
            current_pos = 1
        elif df['short_entry'].iloc[i] == 1 and current_pos == 0:
            current_pos = -1

        if df['long_exit'].iloc[i] == 1 and current_pos == 1:
            current_pos = 0

        if df['short_exit'].iloc[i] == 1 and current_pos == -1:
            current_pos = 0

        trade_state.append(current_pos)

    df['trade_state'] = trade_state

    df["clean_long_entry"] = np.where((df["trade_state"].shift(1) == 0) & (df["trade_state"] == 1),1, 0)
    df["clean_short_entry"] = np.where((df["trade_state"].shift(1) == 0) & (df["trade_state"] == -1),1, 0)

    df["clean_long_exit"] = np.where((df["trade_state"].shift(1) == 1) & (df["trade_state"] == 0),1, 0)
    df["clean_short_exit"] = np.where((df["trade_state"].shift(1) == -1) & (df["trade_state"] == 0),1, 0)

  def run(self):
    super().run()
    self.position()
    self.build_trade_state()


  # def build_trades_list(self):
  #   df = self.data

  #   trades = []
  #   in_position = 0         # 0 = אין עסקה, 1 = לונג, -1 = שורט
  #   entry_index = None

  #   for i in range(len(df)):

  #       # --- כניסה ללונג ---
  #       if df['long_entry'].iloc[i] == 1 and in_position == 0:
  #           in_position = 1
  #           entry_index = i

  #       # --- כניסה לשורט ---
  #       elif df['short_entry'].iloc[i] == 1 and in_position == 0:
  #           in_position = -1
  #           entry_index = i

  #       # --- יציאה מלונג ---
  #       elif in_position == 1 and df['long_exit'].iloc[i] == 1:
  #           trades.append((entry_index, i, 1))
  #           in_position = 0
  #           entry_index = None

  #       # --- יציאה משורט ---
  #       elif in_position == -1 and df['short_exit'].iloc[i] == 1:
  #           trades.append((entry_index, i, -1))
  #           in_position = 0
  #           entry_index = None

  #   self.trades = trades
