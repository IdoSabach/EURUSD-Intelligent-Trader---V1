from data_loader import DataLoad
from indicators import Indicators
from visualizer import Visualizer
from strategy import Strategy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/df60d.csv', parse_dates=['Datetime'], index_col='Datetime')
bot = Strategy(df)
print(bot.data)
bot.run()
print(bot.data)
print(bot.data['position'].value_counts())
viz = Visualizer(bot.data)
viz.plot_entries()