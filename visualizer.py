import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8')
# from strategy import Strategy

class Visualizer():

    def __init__(self, df):
        self.df = df

    def plot_atr(self, atr_col='ATR_14'):
        plt.figure(figsize=(20,5))
        plt.plot(self.df.index, self.df[atr_col], label=atr_col)
        plt.title("ATR Indicator")
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_bollinger(self):
        plt.figure(figsize=(20,8))
        plt.plot(self.df.index, self.df['price'], label="Price", alpha=0.7)
        plt.plot(self.df.index, self.df['BB_upper'], label="Upper Band")
        plt.plot(self.df.index, self.df['BB_mid'], label="Middle Band")
        plt.plot(self.df.index, self.df['BB_lower'], label="Lower Band")
        plt.title("Bollinger Bands")
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_sma(self, sma_list=['SMA_20', 'SMA_100', 'SMA_200']):
        plt.figure(figsize=(20,8))
        plt.plot(self.df.index, self.df['price'], label="Price", alpha=0.5)
        for sma in sma_list:
            if sma in self.df.columns:
                plt.plot(self.df.index, self.df[sma], label=sma)
        plt.title("SMA Indicators")
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_all(self):
        fig, axes = plt.subplots(3, 1, figsize=(22,16), sharex=True)

        # ATR
        axes[0].plot(self.df.index, self.df['ATR_14'], label='ATR_14')
        axes[0].set_title("ATR")
        axes[0].grid(True)

        # Bollinger
        axes[1].plot(self.df.index, self.df['price'], label='Price', alpha=0.7)
        axes[1].plot(self.df.index, self.df['BB_upper'], label='Upper')
        axes[1].plot(self.df.index, self.df['BB_mid'], label='Middle')
        axes[1].plot(self.df.index, self.df['BB_lower'], label='Lower')
        axes[1].set_title("Bollinger Bands")
        axes[1].legend()
        axes[1].grid(True)

        # SMA
        axes[2].plot(self.df.index, self.df['price'], label='Price', alpha=0.5)
        for sma in ['SMA_20', 'SMA_100', 'SMA_200']:
            if sma in self.df.columns:
                axes[2].plot(self.df.index, self.df[sma], label=sma)
        axes[2].set_title("SMA")
        axes[2].legend()
        axes[2].grid(True)

        plt.tight_layout()
        plt.show()

    def plot_strategy_view(self):
        df = self.df

        plt.figure(figsize=(30, 10))

        # === PRICE ===
        plt.plot(df.index, df['price'], label='Price', color='black', linewidth=1.4)

        # === SMA ===
        for col in df.columns:
            if col.startswith("SMA_"):
                plt.plot(df.index, df[col], label=col)

        # === EMA ===
        for col in df.columns:
            if col.startswith("EMA_"):
                plt.plot(df.index, df[col], label=col)

        # === Bollinger Bands ===
        if {'BB_upper','BB_mid','BB_lower'}.issubset(df.columns):
            plt.plot(df.index, df['BB_upper'], label="BB Upper", color='red', alpha=0.6)
            plt.plot(df.index, df['BB_mid'], label="BB Mid", color='yellow', alpha=0.6)
            plt.plot(df.index, df['BB_lower'], label="BB Lower", color='red', alpha=0.6)

        plt.legend()
        plt.grid(True)
        plt.title("Full Strategy View (Price + SMA/EMA + Bollinger)")
        plt.show()

    def plot_entries(self):
        plt.figure(figsize=(18, 8))

        # --- Price + Indicators ---
        plt.plot(self.df.index, self.df['price'], label='Price', linewidth=1)
        plt.plot(self.df.index, self.df['SMA_20'], label='SMA 20', alpha=0.7)
        plt.plot(self.df.index, self.df['SMA_100'], label='SMA 100', alpha=0.7)
        plt.plot(self.df.index, self.df['SMA_200'], label='SMA 200', alpha=0.7)

        # --- Bollinger Bands ---
        plt.plot(self.df.index, self.df['BB_upper'], label='BB Upper', linestyle='--', alpha=0.4)
        plt.plot(self.df.index, self.df['BB_lower'], label='BB Lower', linestyle='--', alpha=0.4)

        # --- Entry/Exit Points ---
        long_entries = self.df[self.df['position'] == 1]
        short_entries = self.df[self.df['position'] == -1]

        # Green dots = LONG
        plt.scatter(long_entries.index, long_entries['price'],
                    marker='^', color='green', s=80, label='LONG Entry')

        # Red dots = SHORT
        plt.scatter(short_entries.index, short_entries['price'],
                    marker='v', color='red', s=80, label='SHORT Entry')

        plt.title("Price + Strategy Entry Signals")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_trades(self):

        plt.figure(figsize=(18, 9))

        # ---- גרף מחיר ----
        plt.plot(self.df.index, self.df['price'], label='Price', color='white', linewidth=1.3)

        # ---- דוגמא לאינדיקטורים (תוסיף מה שיש לך) ----
        if 'SMA_20' in self.df.columns:
            plt.plot(self.df.index, self.df['SMA_20'], label='SMA 20', alpha=0.7)

        if 'SMA_50' in self.df.columns:
            plt.plot(self.df.index, self.df['SMA_100'], label='SMA 50', alpha=0.7)

        if 'BB_upper' in self.df.columns and 'BB_lower' in self.df.columns:
            plt.plot(self.df.index, self.df['BB_upper'], label='Upper BB', alpha=0.5)
            plt.plot(self.df.index, self.df['BB_lower'], label='Lower BB', alpha=0.5)

        # ---- כניסות (1 → long open, -1 → short open) ----
        long_entries = self.df[(self.df['trade_state'] == 1) & (self.df['trade_state'].shift(1) != 1)]
        short_entries = self.df[(self.df['trade_state'] == -1) & (self.df['trade_state'].shift(1) != -1)]

        # ---- יציאות (מעבר מ-1 ל-0 או מ-(-1) ל-0) ----
        long_exits = self.df[(self.df['trade_state'] != 1) & (self.df['trade_state'].shift(1) == 1)]
        short_exits = self.df[(self.df['trade_state'] != -1) & (self.df['trade_state'].shift(1) == -1)]

        # ---- ציור הנקודות ----
        plt.scatter(long_entries.index, long_entries['price'], 
                    marker='^', color='lime', s=120, label='Long Entry')

        plt.scatter(long_exits.index, long_exits['price'], 
                    marker='v', color='red', s=120, label='Long Exit')

        plt.scatter(short_entries.index, short_entries['price'], 
                    marker='v', color='orange', s=120, label='Short Entry')

        plt.scatter(short_exits.index, short_exits['price'], 
                    marker='^', color='yellow', s=120, label='Short Exit')

        # ---- סגנון ----
        plt.title('Price Chart with Trades', fontsize=16)
        plt.legend()
        plt.grid(alpha=0.3)

        plt.show()
