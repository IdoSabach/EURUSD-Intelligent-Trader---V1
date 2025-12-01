import MetaTrader5 as mt5

# התחברות לתוכנה שפתוחה ברקע
if not mt5.initialize():
    print("❌ נכשל בהתחברות ל-MT5")
    print("Error:", mt5.last_error())
    quit()

# קבלת פרטי חשבון
account = mt5.account_info()
if account:
    print("\n=== ✅ חיבור הצליח! ===")
    print(f"מספר חשבון: {account.login}")
    print(f"שרת: {account.server}")
    print(f"יתרה (Balance): ${account.balance}")
    print(f"מינוף: 1:{account.leverage}")
    
    # בדיקת מחיר בזמן אמת
    symbol = "EURUSD"
    tick = mt5.symbol_info_tick(symbol)
    if tick:
        print(f"\nמחיר {symbol} נוכחי:")
        print(f"Mocher (Ask): {tick.ask}")
        print(f"Kone (Bid): {tick.bid}")
    else:
        print(f"\n❌ לא מצליח לקרוא מחיר של {symbol}. בדוק אם השם נכון ב-Market Watch.")
else:
    print("❌ מחובר לתוכנה, אבל לא לחשבון. בדוק ב-MT5 למטה בצד ימין.")

mt5.shutdown()