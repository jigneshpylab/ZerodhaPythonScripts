from kiteconnect import KiteConnect
from math import floor, ceil
import datetime
import pandas as pd
import numpy as np
import sys
import os
import time

dirpath = os.getcwd()

api_key = "api_key"
access_token = "access_token"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

risk_per_trade = 100 # if stoploss gets triggers, you loss will be this, trade quantity will be calculated based on this
slowMA_period = 50
fastMA_period = 21
candlesize = '3minute'

tickerlist = ["HDFCBANK","LT","HDFC","ICICIBANK","LICHSGFIN","CENTURYTEX","SBIN","INDUSINDBK","TATASTEEL","RELIANCE",
              "MARUTI","VEDL","AXISBANK","TATAMOTORS","SIEMENS","TATAMTRDVR","DLF","HINDALCO","M&M","ULTRACEMCO","TATACHEM",
              "L&TFH","AMBUJACEM","UNIONBANK","CANBK","BANKINDIA","VOLTAS","TATAPOWER","GODREJIND","BAJAJ-AUTO","APOLLOTYRE",
              "NCC","RECLTD","BHARATFORG","TATAGLOBAL","PFC","ACC","JSWSTEEL","M&MFIN","BHEL","HEROMOTOCO","ASHOKLEY",
              "BANKBARODA","JINDALSTEL","SRF","ASIANPAINT","UPL","EXIDEIND","ONGC"]
tokenlist = [341249,2939649,340481,1270529,511233,160001,779521,1346049,895745,738561,2815745,784129,1510401,884737,806401,4343041,3771393,348929,519937,2952193,871681,6386689,325121,2752769,2763265,1214721,951809,877057,2796801,4267265,41729,593665,3930881,108033,878593,3660545,5633,3001089,3400961,112129,345089,54273,1195009,1723649,837889,60417,2889473,173057,633601]
NSELTPformate=['NSE:{}'.format(i) for i in tickerlist]


def gethistoricaldata(token):
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(10)
    df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    try:
        data = kite.historical_data(token, startdate, enddate, interval=candlesize)
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
        if not df.empty:
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df['date'] = df['date'].astype(str).str[:-6]
            df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        print("         error in gethistoricaldata", token, e)
    return df

orderslist = []
def run_trategy():
    for i in range(0, len(tickerlist)):
        if (tickerlist[i] in orderslist):
            continue
        try:
            histdata = gethistoricaldata(tokenlist[i])
            histdata["FMA"] = histdata['close'].rolling(fastMA_period).mean()
            histdata["SMA"] = histdata['close'].rolling(slowMA_period).mean()
            FMA = histdata.FMA.values[-10:]
            SMA = histdata.SMA.values[-10:]
            MA_diff =  SMA-FMA

            lastclose = histdata.close.values[-1]
            stoploss_buy = histdata.low.values[-3] # third last candle as stoploss
            stoploss_sell = histdata.high.values[-3] # third last candle as stoploss

            if stoploss_buy > lastclose * 0.996:
                stoploss_buy = lastclose * 0.996 # minimum stoploss as 0.4 %

            if stoploss_sell < lastclose * 1.004:
                stoploss_sell = lastclose * 1.004 # minimum stoploss as 0.4 %
            print(tickerlist[i],lastclose," FMA",FMA[-1], " SMA",SMA[-1], " MA_diff",MA_diff[-1])

            if MA_diff[-1]>0  :#and  MA_diff[-3]< 0 :
                stoploss_buy = lastclose - stoploss_buy
                quantity = floor(max(1, (risk_per_trade/stoploss_buy)))
                target = stoploss_buy*3 # risk reward as 3
                price = int(100 * (floor(lastclose / 0.05) * 0.05)) / 100
                stoploss_buy = int(100 * (floor(stoploss_buy / 0.05) * 0.05)) / 100
                quantity = int(quantity)
                target = int(100 * (floor(target / 0.05) * 0.05)) / 100
                orderslist.append(tickerlist[i])
                order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="BUY",
                                             quantity=quantity,
                                             price=price,
                                             product='MIS',
                                             order_type='LIMIT',
                                             validity='DAY',
                                             trigger_price='0',
                                             squareoff=target,
                                             stoploss=stoploss_buy,
                                             #trailing_stoploss=trailing_loss,
                                             variety="bo"
                                             )
                print("         Order : ", "BUY", tickerlist[i], "quantity:",quantity, "target:",target, "stoploss:",stoploss_buy,datetime.datetime.now())

            if MA_diff[-1] < 0 and MA_diff[-3] > 0:
                stoploss_sell= stoploss_sell - lastclose
                quantity = floor(max(1, (risk_per_trade/stoploss_sell)))
                target = stoploss_sell*3 # risk reward as 3
                price = int(100 * (floor(lastclose / 0.05) * 0.05)) / 100
                stoploss_sell = int(100 * (floor(stoploss_sell / 0.05) * 0.05)) / 100
                quantity = int(quantity)
                target = int(100 * (floor(target / 0.05) * 0.05)) / 100
                orderslist.append(tickerlist[i])
                order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="SELL",
                                             quantity=quantity,
                                             price=price,
                                             product='MIS',
                                             order_type='LIMIT',
                                             validity='DAY',
                                             trigger_price='0',
                                             squareoff=target,
                                             stoploss=stoploss_sell,
                                             #trailing_stoploss=trailing_loss,
                                             variety="bo"
                                             )
                print("         Order : ", "SELL", tickerlist[i], "quantity:",quantity, "target:",target, "stoploss:",stoploss_sell,datetime.datetime.now())
        except Exception as e :
            print(e)
        print("orderslist", orderslist)

def run():
    global runcount
    start_time = int(9) * 60 + int(33)  # specify in int (hr) and int (min) foramte
    end_time = int(15) * 60 + int(10)  # do not place fresh order
    stop_time = int(15) * 60 + int(15)  # square off all open positions
    last_time = start_time
    schedule_interval = 180  # run at every 3 min

    while True:
        if (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) >= end_time:
            if (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) >= stop_time:
                print(sys._getframe().f_lineno, "Trading day closed, time is above stop_time")
                break

        elif (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) >= start_time:
            if time.time() >= last_time:
                last_time = time.time() + schedule_interval
                print("\n\n {} Run Count : Time - {} ".format(runcount, datetime.datetime.now()))
                if runcount >= 0:
                    try:
                        run_trategy()
                    except Exception as e:
                        print("Run error", e)
                runcount = runcount + 1
        else:
            print('     Waiting...', datetime.datetime.now())
            time.sleep(1)
runcount = 0
run()

