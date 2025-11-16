from data_loader import DataLoad
from indicators import Indicators
from visualizer import Visualizer

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/df60d.csv', parse_dates=['Datetime'], index_col='Datetime')

bot = Indicators(df)
bot.run()
print(bot.data)
print(bot.raw_data)
print(bot.data.columns)
viz = Visualizer(bot.data)
viz.plot_all()
viz.plot_strategy_view()