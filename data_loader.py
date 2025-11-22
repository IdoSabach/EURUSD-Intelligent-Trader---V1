import pandas as pd
import numpy as np
import os

class DataLoad:
    """
    Handles data loading, cleaning, and feature engineering (Sessions, Returns).
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def process_data(self):
        """
        Loads data, cleans columns, sets index, calculates returns,
        and defines trading sessions.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # 1. Load File (Handle formats)
        try:
            df = pd.read_csv(self.file_path)
            if len(df.columns) < 2:
                df = pd.read_csv(self.file_path, sep='\t', encoding='utf-16')
        except:
            df = pd.read_csv(self.file_path, sep='\t')

        # 2. Clean Column Names
        df.columns = df.columns.str.strip().str.replace('<', '').str.replace('>', '').str.lower()
        
        # 3. Rename to Standard
        rename_map = {
            'date': 'Date', 'time': 'Time',
            'close': 'price', 'open': 'Open', 'high': 'High', 'low': 'Low',
            'tickvol': 'Volume', 'vol': 'Volume'
        }
        df.rename(columns=rename_map, inplace=True)

        # 4. Datetime Index
        if 'Date' in df.columns and 'Time' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))
        elif 'datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['datetime'])
        else:
            # Fallback search
            date_col = [c for c in df.columns if 'date' in c.lower()]
            if date_col:
                df['Datetime'] = pd.to_datetime(df[date_col[0]])
            else:
                raise KeyError("Date/Time columns missing.")

        df.set_index('Datetime', inplace=True)
        df.sort_index(inplace=True)

        df = df[~df.index.duplicated(keep='first')]
        
        # 5. Calculate Returns
        df['returns'] = np.log(df['price'] / df['price'].shift(1))
        
        # 6. --- Define Sessions (Added Back) ---
        # We use vectorization (np.select) for speed instead of loops
        hours = df.index.hour
        
        conditions = [
            (hours >= 2) & (hours < 10),   # Asia
            (hours >= 10) & (hours < 15),  # London
            (hours >= 15) & (hours <= 23), # NY
            (hours >= 0) & (hours < 2)     # Deadzone
        ]
        
        choices = ['asia', 'london', 'ny', 'deadzone']
        
        # Assign session column
        df['session'] = np.select(conditions, choices, default='deadzone')

        # 7. Final Cleanup
        required_cols = ['price', 'High', 'Low', 'returns', 'session']
        self.data = df[required_cols].dropna().copy()
        
        return self.data