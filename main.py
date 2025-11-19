from data_loader import DataLoad
from indicators import Indicators
from visualizer import Visualizer
from strategy import Strategy
from backtester import Backtester

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/df60d.csv', parse_dates=['Datetime'], index_col='Datetime')
bot = Backtester(df)
bot.run_backtest()
print(bot.data)
viz = Visualizer(bot.data)

bot.data.to_csv("data/results.csv", index=False)

# viz.plot_trades()
bot.summary()



