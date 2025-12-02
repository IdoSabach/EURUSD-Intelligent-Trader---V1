import MetaTrader5 as mt5
import pandas as pd
import time
import datetime
import json
import os
from strategy import Strategy
from telegram_notify import send_telegram_msg 

SYMBOL = "EURUSD"       
TIMEFRAME = mt5.TIMEFRAME_H1
VOLUME = 0.01           
DEVIATION = 10          
MAGIC_NUMBER = 999001   
PARAMS_FILE = "best_params.json"

def load_best_params():
    """טוען את הפרמטרים המנצחים מהקובץ שיצר ה-Optimizer"""
    if not os.path.exists(PARAMS_FILE):
        print(f"❌ Error: '{PARAMS_FILE}' not found!")
        print("Please run 'main.py' first to generate strategy parameters.")
        quit()
        
    with open(PARAMS_FILE, "r") as f:
        params = json.load(f)
    
    print(f"\n✅ Loaded Strategy Parameters from {PARAMS_FILE}")
    return params

def initialize_mt5():
    if not mt5.initialize():
        print("❌ MT5 Initialize failed")
        quit()
    
    account = mt5.account_info()
    if not account:
        print("❌ Not connected to account")
        quit()
        
    msg = f"🤖 <b>Bot Started Successfully!</b>\nAsset: {SYMBOL}\nMode: Auto-JSON Params"
    print(msg)
    send_telegram_msg(msg)

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
    positions = mt5.positions_get(symbol=SYMBOL)
    for pos in positions:
        if pos.magic == MAGIC_NUMBER:
            return

    order_type = mt5.ORDER_TYPE_BUY if signal == 1 else mt5.ORDER_TYPE_SELL
    type_str = "BUY 🟢" if signal == 1 else "SELL 🔴"
    
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
        "comment": "Algo-Pro Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        msg = f"""
🚀 <b>New Trade Opened!</b>
---------------------
<b>Type:</b> {type_str}
<b>Price:</b> {price}
<b>SL:</b> {sl:.5f}
<b>TP:</b> {tp:.5f}
<b>Size:</b> {VOLUME}
        """
        print(msg)
        send_telegram_msg(msg)
    else:
        print("❌ Order Failed:", result.comment)

def run_live():
    strategy_params = load_best_params()
    
    # 2. חיבור
    initialize_mt5()
    
    hourly_msg_sent = False
    
    while True:
        try:
            now = datetime.datetime.now()

            if now.minute == 0 and not hourly_msg_sent:
                tick = mt5.symbol_info_tick(SYMBOL)
                account = mt5.account_info()
                current_price = (tick.ask + tick.bid) / 2
                
                status_msg = f"""
⏱ <b>Hourly Update ({now.strftime('%H:%M')})</b>
---------------------
✅ Status: <b>Running</b>
💶 Price: {current_price:.5f}
💰 Equity: ${account.equity}
---------------------
                """
                send_telegram_msg(status_msg)
                print(f"Sent hourly update at {now}")
                hourly_msg_sent = True 
            
            elif now.minute != 0:
                hourly_msg_sent = False

            df = get_live_data()
            if df is None:
                time.sleep(10)
                continue

            strategy = Strategy(df, params=strategy_params)
            strategy.run_strategy()
            
            last_candle = strategy.data.iloc[-2]
            signal = last_candle['position']
            
            print(f"\r⏳ {now.strftime('%H:%M:%S')} | Price: {last_candle['price']:.5f} | Signal: {signal} ", end="")
            
            if signal != 0:
                tick = mt5.symbol_info_tick(SYMBOL)
                market_price = tick.ask if signal == 1 else tick.bid
                
                if signal == 1:
                    sl = last_candle['long_sl_val']
                    tp = last_candle['long_tp_val']
                else:
                    sl = last_candle['short_sl_val']
                    tp = last_candle['short_tp_val']
                
                execute_trade(signal, market_price, sl, tp)
                print("💤 Signal processed. Sleeping for 1 hour...")
                time.sleep(3600) 
            
            time.sleep(60)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            send_telegram_msg(f"⚠️ <b>CRITICAL ERROR</b>\nBot crashed: {e}")
            time.sleep(10)

import traceback

if __name__ == "__main__":
    try:
        run_live()
        
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user.")
        send_telegram_msg("🛑 <b>Bot Stopped Manually</b>")
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print("❌ CRITICAL ERROR OCCURRED!")
        print(error_trace)
        
        crash_msg = f"""
⚠️ <b>CRITICAL ALERT: BOT CRASHED!</b>
-----------------------------
The bot stopped working.
<b>Error:</b> {str(e)}
-----------------------------
Restarting automatically in 5 seconds...
        """
        send_telegram_msg(crash_msg)
        
        raise e




# import MetaTrader5 as mt5
# import pandas as pd
# import time
# import datetime
# import json
# import os
# from strategy import Strategy
# from telegram_notify import send_telegram_msg 

# # ==========================================
# # ⚙️ הגדרות ברוקר
# # ==========================================
# SYMBOL = "EURUSD"       
# TIMEFRAME = mt5.TIMEFRAME_H1
# VOLUME = 0.01           
# DEVIATION = 10          
# MAGIC_NUMBER = 999001   
# PARAMS_FILE = "best_params.json"
# # ==========================================

# def load_best_params():
#     if not os.path.exists(PARAMS_FILE):
#         print(f"❌ Error: '{PARAMS_FILE}' not found!")
#         quit()
#     with open(PARAMS_FILE, "r") as f:
#         return json.load(f)

# def initialize_mt5():
#     if not mt5.initialize():
#         print("❌ MT5 Initialize failed")
#         quit()
#     account = mt5.account_info()
#     if not account:
#         print("❌ Not connected to account")
#         quit()
    
#     # הודעת פתיחה - מצב בדיקה
#     msg = f"🧪 <b>TEST MODE STARTED!</b>\nSending msgs every 10s..."
#     print(msg)
#     send_telegram_msg(msg)

# def get_live_data():
#     rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 500)
#     if rates is None: return None
#     df = pd.DataFrame(rates)
#     df['time'] = pd.to_datetime(df['time'], unit='s')
#     rename = {'time': 'Datetime', 'close': 'price', 'high': 'High', 'low': 'Low', 'open': 'Open', 'tick_volume': 'Volume'}
#     df.rename(columns=rename, inplace=True)
#     df.set_index('Datetime', inplace=True)
#     return df

# def execute_trade(signal, price, sl, tp):
#     positions = mt5.positions_get(symbol=SYMBOL)
#     for pos in positions:
#         if pos.magic == MAGIC_NUMBER:
#             return

#     order_type = mt5.ORDER_TYPE_BUY if signal == 1 else mt5.ORDER_TYPE_SELL
    
#     request = {
#         "action": mt5.TRADE_ACTION_DEAL,
#         "symbol": SYMBOL,
#         "volume": VOLUME,
#         "type": order_type,
#         "price": price,
#         "sl": sl,
#         "tp": tp,
#         "deviation": DEVIATION,
#         "magic": MAGIC_NUMBER,
#         "comment": "Algo-Pro Test",
#         "type_time": mt5.ORDER_TIME_GTC,
#         "type_filling": mt5.ORDER_FILLING_IOC,
#     }

#     result = mt5.order_send(request)
#     if result.retcode == mt5.TRADE_RETCODE_DONE:
#         msg = f"🚀 TEST TRADE OPENED! Price: {price}"
#         send_telegram_msg(msg)
#         print(msg)

# def run_live():
#     params = load_best_params()
#     initialize_mt5()
    
#     while True:
#         try:
#             now = datetime.datetime.now()

#             # --- 🔔 בדיקת דופק מהירה (TEST) ---
#             # אין תנאי של שעה! שולח תמיד.
#             tick = mt5.symbol_info_tick(SYMBOL)
#             price_str = f"{tick.bid:.5f}" if tick else "Unknown"
            
#             status_msg = f"🚀 <b>TEST ALIVE</b> ({now.strftime('%H:%M:%S')})\nPrice: {price_str}"
#             print(status_msg)
#             send_telegram_msg(status_msg)
#             # ----------------------------------

#             # --- לוגיקת המסחר (עדיין עובדת ברקע) ---
#             df = get_live_data()
#             if df is not None:
#                 strategy = Strategy(df, params=params)
#                 strategy.run_strategy()
#                 last_candle = strategy.data.iloc[-2]
#                 signal = last_candle['position']
                
#                 if signal != 0:
#                     tick = mt5.symbol_info_tick(SYMBOL)
#                     market_price = tick.ask if signal == 1 else tick.bid
                    
#                     # חישוב סטופים
#                     if signal == 1:
#                         sl = last_candle['long_sl_val']
#                         tp = last_candle['long_tp_val']
#                     else:
#                         sl = last_candle['short_sl_val']
#                         tp = last_candle['short_tp_val']
                    
#                     execute_trade(signal, market_price, sl, tp)
            
#             # המתנה קצרה של 10 שניות בלבד לבדיקה
#             time.sleep(10)

#         except Exception as e:
#             print(f"\n❌ Error: {e}")
#             time.sleep(5)

# if __name__ == "__main__":
#     run_live()