import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8')

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
