import MetaTrader5 as mt5
import pandas as pd
import time
import datetime
import json
import os
from strategy import Strategy

# ==========================================
# ⚙️ הגדרות ברוקר וניהול
# ==========================================
SYMBOL = "EURUSD"       
TIMEFRAME = mt5.TIMEFRAME_H1
VOLUME = 0.02        # גודל פוזיציה קבוע (מיקרו לוט)
DEVIATION = 10          
MAGIC_NUMBER = 999001   
PARAMS_FILE = "best_params.json"
# ==========================================

def load_best_params():
    """טוען את הפרמטרים המנצחים מהקובץ שיצר ה-Optimizer"""
    if not os.path.exists(PARAMS_FILE):
        print(f"❌ Error: '{PARAMS_FILE}' not found!")
        print("Please run 'main.py' first to generate strategy parameters.")
        quit()
        
    with open(PARAMS_FILE, "r") as f:
        params = json.load(f)
    
    print("\n✅ Loaded Strategy Parameters:")
    print(json.dumps(params, indent=4))
    return params

def initialize_mt5():
    if not mt5.initialize():
        print("❌ MT5 Initialize failed, error:", mt5.last_error())
        quit()
    
    account = mt5.account_info()
    if not account:
        print("❌ Failed to get account info. Please login to MT5.")
        quit()
        
    print(f"\n=== 🟢 LIVE TRADER CONNECTED ===")
    print(f"Account: {account.login} | Server: {account.server}")
    print(f"Balance: ${account.balance} | Equity: ${account.equity}")
    print("================================")

def get_live_data():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 500)
    if rates is None: return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    rename = {'time': 'Datetime', 'close': 'price', 'high': 'High', 'low': 'Low', 'open': 'Open', 'tick_volume': 'Volume'}
    df.rename(columns=rename, inplace=True)
    df.set_index('Datetime', inplace=True)
    return df

def execute_trade(signal, price, sl, tp):
    # בדיקת עסקאות קיימות
    positions = mt5.positions_get(symbol=SYMBOL)
    for pos in positions:
        if pos.magic == MAGIC_NUMBER:
            print("⚠️ Bot position already open. Waiting...")
            return

    order_type = mt5.ORDER_TYPE_BUY if signal == 1 else mt5.ORDER_TYPE_SELL
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": VOLUME,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": DEVIATION,
        "magic": MAGIC_NUMBER,
        "comment": "Algo-Pro AI",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    print(f"🚀 EXECUTING { 'BUY' if signal==1 else 'SELL' } | SL: {sl:.5f} | TP: {tp:.5f}")
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("❌ Order Failed:", result.comment)
    else:
        print(f"✅ Order Placed! Ticket: {result.order}")

def run_live():
    # 1. טעינת המוח
    params = load_best_params()
    
    # 2. חיבור לגוף
    initialize_mt5()
    
    print(f"🤖 Bot is running on {SYMBOL} (H1)...")
    
    while True:
        try:
            # משיכת נתונים
            df = get_live_data()
            if df is None:
                time.sleep(10)
                continue

            # חישוב אסטרטגיה
            strategy = Strategy(df, params=params)
            strategy.run_strategy()
            
            # בדיקת הנר האחרון שנסגר (לפני אחרון)
            last_candle = strategy.data.iloc[-2]
            signal = last_candle['position']
            price = last_candle['price']
            
            # הדפסת סטטוס
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"\r⏳ {timestamp} | Close: {price:.5f} | Signal: {signal} ", end="")
            
            if signal != 0:
                print("\n💡 SIGNAL RECEIVED!")
                
                # קבלת מחיר שוק עדכני לביצוע
                tick = mt5.symbol_info_tick(SYMBOL)
                market_price = tick.ask if signal == 1 else tick.bid
                
                # שליפת יעדים
                if signal == 1:
                    sl = last_candle['long_sl_val']
                    tp = last_candle['long_tp_val']
                else:
                    sl = last_candle['short_sl_val']
                    tp = last_candle['short_tp_val']
                
                execute_trade(signal, market_price, sl, tp)
                
                # מניעת כפילות - לישון עד הנר הבא
                print("💤 Signal processed. Sleeping for 1 hour...")
                time.sleep(3600) 
            
            time.sleep(60)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_live()