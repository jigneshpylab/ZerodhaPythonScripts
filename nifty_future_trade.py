from kiteconnect import KiteConnect
import datetime
import pandas as pd
import time

"""
1. set your zerodha credentials
"""
api_key = "your api_key"
access_token = "your access_token"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)
"""
2. Get instrument token of near month nifty future
"""
print("Downloading instrument tokens..........", datetime.datetime.now())
df = pd.read_csv("https://api.kite.trade/instruments")
df = df[df['segment'] == "NFO-FUT"]
df = df[~df['tradingsymbol'].str.startswith("{}".format("NIFTYIT"))]
df = df[df['tradingsymbol'].str.startswith("{}".format("NIFTY"))]
df['expiry'] = pd.to_datetime(df['expiry'])
tday = pd.Timestamp.today() - pd.DateOffset(0)
df = df[~(df['expiry'] <= tday)]
df = df[df.expiry == df.expiry.min()]
print("\n", df)
print("Instrument tokens Downloaded..........", datetime.datetime.now())
token_nifty_future = df.instrument_token.values[0]
tradingsymbol_nifty_future = df.tradingsymbol.values[0]
print("\ntoken_nifty_future",token_nifty_future)
print("tradingsymbol_nifty_future",tradingsymbol_nifty_future)

"""
3. set your logic to buy or sell
"""
def get_signal(data=None):
    """
    you need to implement your idea to generate buy or sell signal from given data.
    signal can be from any logic, e.g. conventional technical analysis or price-action or machine learning or any other.

    :param data: data can be any values required for your strategy calculations
    :return: "BUY" or "SELL or None
    """
    # sample logic, data in LTP in this sample
    LTP = data
    signal = None
    if LTP<7545.0 :
        signal = 'SELL'
    elif LTP > 8270.0 :
        signal = 'BUY'
    return  signal

"""
4. set trade time
"""
opentime = int(9) * 60 + int(16)
closetime = int(15) * 60 + int(30)
timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Waiting for market to open..........", datetime.datetime.now())

"""
5. download price, evaluate logic and place order
"""

while timenow < opentime:
    time.sleep(0.2)
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Market opened..........", datetime.datetime.now())

orderplaced = False
while orderplaced == False :
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
    if timenow >= closetime:
        print("Market Closed.........", datetime.datetime.now())
        keep_running = False
        break
    try :
        LTP = kite.ltp('NFO:{}'.format(tradingsymbol_nifty_future))['NFO:{}'.format(tradingsymbol_nifty_future)]['last_price'] # This call downloads LTP from zerodha kite conncet API
        LTP = int(LTP)
        print(tradingsymbol_nifty_future, "LTP:",LTP, datetime.datetime.now())
        signal = get_signal(LTP) # this statement pass data in function get_signal and return the signal
        if signal == 'BUY' or signal == 'SELL':
            try:
                    orderid = kite.place_order(exchange='NFO',
                                                tradingsymbol=tradingsymbol_nifty_future,
                                                transaction_type=signal,
                                                quantity=int(75), # set the quantity in numptiple of lot size
                                                #price=LTP,
                                                product='NRML',
                                                order_type='MARKET', # you can keep as LIMIT
                                                validity='DAY',
                                                trigger_price='0',
                                                variety="regular"
                                                )
                    print("Order  Placed : ", signal, tradingsymbol_nifty_future, "LTP", LTP,'orderid',orderid, datetime.datetime.now())
                    orderplaced = True

            except Exception as e:
                    print(e)
                    
            break # break while loop once order is placed
    except Exception as e:
        print(e)
print("Run Completed ..........", datetime.datetime.now())
