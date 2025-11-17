import numpy as np
import pandas as pd
from data_loader import DataLoad

class Indicators(DataLoad):
  def __init__(self, df):
    super().__init__(df)
    self.process_data()

  def sma(self, period):
    '''
    Calculate a Sma \n
    period: num of last candle mean
    '''
    self.data[f"SMA_{period}"] = self.data['price'].rolling(period).mean()
    return self.data
  
  def bollinger(self, period=20, std=2):
    '''
    Calculate a BB = Bollinger Bands \n
    period: default 20 (sma) \n
    std: default 2 (std)
    '''
    ma = self.data['price'].rolling(period).mean()
    sd = self.data['price'].rolling(period).std()

    self.data['BB_mid'] = ma
    self.data['BB_upper'] = ma + std * sd 
    self.data['BB_lower'] = ma - std * sd

    return self.data
  
  def atr(self, period=14):
    '''
    Calculate a ATR \n
    period: default 20 (sma)
    '''
    df = self.data

    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = np.abs(df['High'] - df['price'].shift(1))
    df['L-PC'] = np.abs(df['Low'] - df['price'].shift(1))

    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df[f"ATR_{period}"] = df['TR'].rolling(period).mean()

    df.drop(columns=['H-L','H-PC','L-PC','TR'], axis=1, inplace=True, errors='ignore')

  
  def run(self):
    self.sma(20)
    self.sma(100)
    self.sma(200)
    self.bollinger()
    self.atr()
    self.data.dropna(inplace=True)
    

  
  

