import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

df = pd.read_csv('data/df60d.csv', index_col=0, parse_dates=True)

class DataLoad():
  def __init__(self, df):
    self.raw_data = df
    self.data = df

  def process_data(self):
    df = self.data.copy()

    df = df.rename(columns={'Close':'price'})
    df['returns'] = np.log(df['price'] / df['price'].shift(1))

    # convert column to date type
    df.index = pd.to_datetime(df.index)
    df['hour'] = df.index.hour
    df['date'] = df.index.date  

    df.dropna(inplace=True)
    self.data = df   
    return self.data

  def split_sessions(self):
    df = self.data.copy()

    # split all df to 4 main sessions
    self.df_asia = df[(df['hour'] >= 2) & (df['hour'] < 10)]
    self.df_london = df[(df['hour'] >= 10) & (df['hour'] < 18)]
    self.df_ny = df[(df['hour'] >= 15) & (df['hour'] <= 23)]
    self.df_deadzone = df[(df['hour'] >= 0) & (df['hour'] < 2)]

    sessions = {
      'asia' : self.df_asia,
      'london' : self.df_london,
      'ny' : self.df_ny,
      'deadzone' : self.df_deadzone
    }

    return sessions
  
  def run(self):
    self.process_data()
    self.split_sessions()
  
