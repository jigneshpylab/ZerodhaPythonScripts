from kiteconnect import KiteConnect
from math import floor
import datetime
import pandas as pd
import os
import time

dirpath = os.getcwd()
pd.set_option('display.max_columns',20)
print("\nRun Started.......... : ", datetime.datetime.now())
"""
1. Login to kite
keep you login credential data in userdata.csv at given path for all accounts 
"""
userdata = pd.read_csv("C://db//loginkey//userdata.csv")
allusers = len(userdata.index.values)
kites = [None] * allusers

risk_per_trade = 100 # if stoploss gets triggers, you loss will be this, trade quantity will be calculated based on this


for i in range(0, allusers):
    try:
        api_key = userdata.loc[i, "api_key"]
        api_secret = userdata.loc[i, "api_secret"]
        request_token = userdata.loc[i, "request_token"]
        access_token = userdata.loc[i, "access_token"]
        public_token = userdata.loc[i, "public_token"]
        kitei = KiteConnect(api_key=api_key)
        kitei.set_access_token(access_token)
        kites[i] = kitei
    except Exception as e:
        print(" ERROR in api_key", i, e, datetime.datetime.now())
print("user data loaded..........", datetime.datetime.now())

tickerlist = ["ACC","ADANIENT","ADANIPORTS","ADANIPOWER","AMARAJABAT","AMBUJACEM","APOLLOHOSP","APOLLOTYRE","ASHOKLEY","ASIANPAINT","AUROPHARMA","AXISBANK","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BALKRISIND","BANKBARODA","BATAINDIA","BEL","BERGEPAINT","BHARATFORG","BHARTIARTL","BHEL","BIOCON","BOSCHLTD","BPCL","BRITANNIA","CADILAHC","CANBK","CASTROLIND","CENTURYTEX","CESC","CHOLAFIN","CIPLA","COALINDIA","COLPAL","CONCOR","CUMMINSIND","DABUR","DISHTV","DIVISLAB","DLF","DRREDDY","EICHERMOT","EQUITAS","ESCORTS","EXIDEIND","FEDERALBNK","GAIL","GLENMARK","GMRINFRA","GODREJCP","GRASIM","HAVELLS","HCLTECH","HDFC","HDFCBANK","HEROMOTOCO","HEXAWARE","HINDALCO","HINDPETRO","HINDUNILVR","IBULHSGFIN","ICICIBANK","ICICIPRULI","IDEA","IDFCFIRSTB","IGL","INDIGO","INDUSINDBK","INFRATEL","INFY","IOC","ITC","JINDALSTEL","JSWSTEEL","JUBLFOOD","JUSTDIAL","KOTAKBANK","L&TFH","LICHSGFIN","LT","LUPIN","M&M","M&MFIN","MANAPPURAM","MARICO","MARUTI","MCDOWELL-N","MFSL","MGL","MINDTREE","MOTHERSUMI","MRF","MUTHOOTFIN","NATIONALUM","NBCC","NCC","NESTLEIND","NIITTECH","NMDC","NTPC","OIL","ONGC","PAGEIND","PEL","PETRONET","PFC","PIDILITIND","PNB","POWERGRID","PVR","RAMCOCEM","RBLBANK","RECLTD","RELIANCE","SAIL","SBIN","SHREECEM","SIEMENS","SRF","SRTRANSFIN","SUNPHARMA","SUNTV","TATACHEM","TATAELXSI","TATAGLOBAL","TATAMOTORS","TATAMTRDVR","TATAPOWER","TATASTEEL","TCS","TECHM","TITAN","TORNTPHARM","TORNTPOWER","TVSMOTOR","UBL","UJJIVAN","ULTRACEMCO","UNIONBANK","UPL","VEDL","VOLTAS","WIPRO","YESBANK","ZEEL"]
NSELTPformate=['NSE:{}'.format(i) for i in tickerlist]

algoruntime = int(9) * 60 + int(17) # set time when you want to check for top gainer and losers to place orders
nums_buy = 5 # number of stock to buy
nums_sell = 5 # number of stock to sell
target = 2 # as %
stoploss =  1  # as %
trailing_stoploss = 0.5 # as %
filterstock_lowpricelimit = 100
filterstock_highpricelimit = 2000

try:
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
    print("\nWaiting for time 9:18..........", datetime.datetime.now())

    while timenow < algoruntime:
        time.sleep(10)
        timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
        #print("Waiting to get open price..........", datetime.datetime.now())


    OHLCdict = kites[0].ohlc(NSELTPformate)
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
            #print(c1,c2,c3,c4,c5,c6,c7)
            if c3 > filterstock_lowpricelimit and c3 < filterstock_highpricelimit :
                OHLCdf.loc[len(OHLCdf)] = [c1,c2,c3,c4,c5,c6,c7,c3-c7,100*(c3-c7)/c7]
        except Exception as e:
            print(e)
    OHLCdf = OHLCdf.sort_values(by=['pchange'],ascending=False)
    OHLCdf_buy = OHLCdf.head(nums_buy)
    OHLCdf_sell = OHLCdf.tail(nums_sell)
    print("\n\nTOP gainer\n", OHLCdf_buy)
    print("\n\nTop loser\n", OHLCdf_sell)
except Exception as e:
    print("ERROR in RUN ", e)

orderslist = [0,0] # keep token of stocks that you want to skip

def run_trategy_long():
    tickerstobuy = OHLCdf_buy.tradingsymbol.values
    tickerstobuy_ltp = OHLCdf_buy.last_price.values
    tickerstobuy_token = OHLCdf_buy.instrument_token.values
    for inx, i in enumerate(tickerstobuy_token):
        if i in set(orderslist):
            #print("Checking if ",i,"in", orderslist)
            continue
        else:
            your_custom_conditions = True # apply your strategy
            try :
                if your_custom_conditions == True :
                        orderslist.append(i)

                        buyprice = tickerstobuy_ltp[inx]
                        buy_target = buyprice * target/100
                        buy_stoploss = buyprice * stoploss/100
                        buy_trailing_stoploss = buyprice * trailing_stoploss/100


                        buyprice = int(100 * (floor(buyprice / 0.05) * 0.05)) / 100
                        buy_target = int(100 * (floor(buy_target / 0.05) * 0.05)) / 100
                        buy_stoploss = int(100 * (floor(buy_stoploss / 0.05) * 0.05)) / 100
                        quantity = int(floor(max(1, (risk_per_trade / buy_stoploss))))

                        for ki in range(0, allusers):
                            try:
                                print("\n\nBUY Order",
                                      "\ntradingsymbol", tickerstobuy[inx],
                                      "\nquantity:", quantity,
                                      "\nbuyprice:", buyprice,
                                      "\nbuy_target :", buy_target,
                                      "\nbuy_stoploss:", buy_stoploss, " Time : ", datetime.datetime.now())

                                orderid_b = kites[ki].place_order(exchange='NSE',
                                                             tradingsymbol=tickerstobuy[inx],
                                                             transaction_type="BUY",
                                                             quantity=quantity,
                                                             price=buyprice,
                                                             product='MIS',
                                                             order_type='LIMIT',
                                                             validity='DAY',
                                                             trigger_price='0',
                                                             # disclosed_quantity=None,
                                                             squareoff=buy_target,
                                                             stoploss=buy_stoploss,
                                                             trailing_stoploss=buy_trailing_stoploss,
                                                             variety="bo"
                                                             )

                                print("BUY Order is placed : orderid ", orderid_b)
                            except Exception as e:
                                print("BUY ORDER FAILED : RESPONSE FROM ZERODHA : ", e)
            except Exception as e :
                print(e)
                pass
run_trategy_long()

def run_trategy_short():
    tickerstosell = OHLCdf_sell.tradingsymbol.values
    tickerstosell_ltp = OHLCdf_sell.last_price.values
    tickerstosell_token = OHLCdf_sell.instrument_token.values
    for inx, i in enumerate(tickerstosell_token):
        if i in orderslist:
            continue
        else:
            your_custom_conditions = True # apply your strategy
            try :
                if your_custom_conditions == True :
                        orderslist.append(i)

                        sellprice = tickerstosell_ltp[inx]
                        sell_target =  sellprice * target/100
                        sell_stoploss = sellprice * stoploss/100
                        sell_trailing_stoploss = sellprice * trailing_stoploss / 100

                        sellprice = int(100 * (floor(sellprice / 0.05) * 0.05)) / 100
                        sell_target = int(100 * (floor(sell_target / 0.05) * 0.05)) / 100
                        sell_stoploss = int(100 * (floor(sell_stoploss / 0.05) * 0.05)) / 100
                        sell_trailing_stoploss = int(100 * (floor(sell_trailing_stoploss / 0.05) * 0.05)) / 100
                        quantity = int(floor(max(1, (risk_per_trade / sell_stoploss))))

                        for ki in range(0, allusers):
                            try:
                                print("\n\n SELL Order",
                                      "\ntradingsymbol",tickerstosell[inx],
                                      "\n quantity:", sell_stoploss,
                                      "\n price:", sellprice,
                                      "\n sell target :", sell_target,
                                      "\n sell stoploss:", sell_stoploss, " Time : ", datetime.datetime.now())

                                orderid_s = kites[ki].place_order(exchange='NSE',
                                                             tradingsymbol=tickerstosell[inx],
                                                             transaction_type="SELL",
                                                             quantity=quantity,
                                                             price=sellprice,
                                                             product='MIS',
                                                             order_type='LIMIT',
                                                             validity='DAY',
                                                             trigger_price='0',
                                                             # disclosed_quantity=None,
                                                             squareoff=sell_target,
                                                             stoploss=sell_stoploss,
                                                             trailing_stoploss=sell_trailing_stoploss,
                                                             variety="bo"
                                                             )

                                print("SELL Order is placed : orderid ", orderid_s," Time : ", datetime.datetime.now())
                            except Exception as e:
                                print("SELL ORDER FAILED : RESPONSE FROM ZERODHA : ", e)

            except Exception as e :
                print(e)
                pass
run_trategy_short()
