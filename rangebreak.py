from kiteconnect import KiteConnect
from math import floor
import datetime
import pandas as pd
import time

api_key = "your api_key"
access_token = "your access_token"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

risk_per_trade = 100 # if stoploss gets triggers, you loss will be this, trade quantity will be calculated based on this
tickerlist = ["HDFCBANK","LT","HDFC","ICICIBANK","LICHSGFIN"] # you can keep any number of stocks, symbol must match with zerodha trading symbol
NSELTPformat=['NSE:{}'.format(i) for i in tickerlist]

orderplacetime = int(9) * 60 + int(6) # as int(hr) +60 * int(min):

timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("\nWaiting for time 9:30..........", datetime.datetime.now())
while timenow < orderplacetime:
    time.sleep(1)
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)

OHLCdict = kite.ohlc(NSELTPformat)
print(OHLCdict)
OHLCdf = pd.DataFrame(columns=['tradingsymbol', 'instrument_token', 'last_price','open','high', 'low', 'close','change','pchange'])

for key, value in OHLCdict.items():
        try:
            c1 = key.split(":")[1]
            c2 = value['instrument_token']
            c3 = value['last_price']
            value2 = value['ohlc']
            c4 = value2['open']
            c5 = value2['high']
            c6 = value2['low']
            c7 = value2['close']
            OHLCdf.loc[len(OHLCdf)] = [c1,c2,c3,c4,c5,c6,c7,c3-c7,100*(c3-c7)/c7]
        except Exception as e:
            print(e)
print(OHLCdf)
for i in range(0, len(OHLCdf)):
    try :
        dfi = OHLCdf.iloc[i]
        #print(dfi)
        try:
                tradingsymbol = dfi['tradingsymbol']
                highlimit = dfi['high']
                lowlimit = dfi['low']
                stoploss = highlimit-lowlimit
                quantity = int(floor(max(1, (risk_per_trade / stoploss))))

                buy_limit = highlimit*1.03
                buy_target = highlimit*1.09
                sell_limit = lowlimit*0.97
                sell_target = lowlimit*0.91

                buy_limit = int(100 * (floor(buy_limit / 0.05) * 0.05)) / 100
                buy_target = int(100 * (floor(buy_target / 0.05) * 0.05)) / 100
                sell_limit = int(100 * (floor(sell_limit / 0.05) * 0.05)) / 100
                sell_target = int(100 * (floor(sell_target / 0.05) * 0.05)) / 100
                stoploss = int(100 * (floor(stoploss / 0.05) * 0.05)) / 100
                print("\n", tradingsymbol, "highlimit",highlimit, "lowlimit",lowlimit, "stoploss",stoploss, "quantity",quantity)
                try :
                    buyid = kite.place_order(exchange='NSE', tradingsymbol=tradingsymbol,
                                                      transaction_type="BUY",
                                                      quantity=quantity,
                                                      price=buy_limit,
                                                      product='MIS',
                                                      order_type='SL',
                                                      validity='DAY',
                                                      trigger_price=highlimit,
                                                      squareoff=buy_target,
                                                      stoploss=stoploss,
                                                      variety="bo")

                    print(buyid)
                except Exception as e:
                    print(e)

                try :
                    sellid = kite.place_order(exchange='NSE', tradingsymbol=tradingsymbol,
                                                      transaction_type="SELL",
                                                      quantity=quantity,
                                                      price=sell_limit,
                                                      product='MIS',
                                                      order_type='SL',
                                                      validity='DAY',
                                                      trigger_price=lowlimit,
                                                      squareoff=sell_target,
                                                      stoploss=stoploss,
                                                      variety="bo")
                    print(sellid)
                except Exception as e:
                    print(e)
        except Exception as e:
                print(e)
    except Exception as e:
        print(e)




