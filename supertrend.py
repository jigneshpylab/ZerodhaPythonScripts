from kiteconnect import KiteConnect
from math import floor, ceil
import datetime
import pandas as pd
import numpy as np
import sys
import os
import time

dirpath = os.getcwd()
pd.set_option('display.max_columns',20)
print("\nRun Started.......... : ", datetime.datetime.now())

"""
1. Login to kite
"""
userdata = pd.read_csv("C://db//loginkey//userdata.csv")
#userdata = pd.read_csv("{}/userdata.csv".format(dirpath))
mainuser = userdata.head(1)["user"].values[0]

allusers = len(userdata.index.values)
kites = [None] * allusers

risk_per_trade = 100 # if stoploss gets triggers, you loss will be this, trade quantity will be calculated based on this
supertrend_period = 30
supertrend_multiplier=3
candlesize = '5minute'



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

#list all tickers you want to trade
tickerlist = ["HDFCBANK","LT","HDFC","ICICIBANK","LICHSGFIN","CENTURYTEX","SBIN","INDUSINDBK","TATASTEEL","RELIANCE","MARUTI","VEDL","AXISBANK","TATAMOTORS","SIEMENS","TATAMTRDVR","DLF","HINDALCO","M&M","ULTRACEMCO","TATACHEM","L&TFH","AMBUJACEM","UNIONBANK","CANBK","BANKINDIA","VOLTAS","TATAPOWER","GODREJIND","BAJAJ-AUTO","APOLLOTYRE","NCC","RECLTD","BHARATFORG","TATAGLOBAL","PFC","ACC","JSWSTEEL","M&MFIN","BHEL","HEROMOTOCO","ASHOKLEY","BANKBARODA","JINDALSTEL","SRF","ASIANPAINT","UPL","EXIDEIND","ONGC"]
tokenlist = [341249,2939649,340481,1270529,511233,160001,779521,1346049,895745,738561,2815745,784129,1510401,884737,806401,4343041,3771393,348929,519937,2952193,871681,6386689,325121,2752769,2763265,1214721,951809,877057,2796801,4267265,41729,593665,3930881,108033,878593,3660545,5633,3001089,3400961,112129,345089,54273,1195009,1723649,837889,60417,2889473,173057,633601]
NSELTPformate=['NSE:{}'.format(i) for i in tickerlist]



# Source for tech indicator : https://github.com/arkochhar/Technical-Indicators/blob/master/indicator/indicators.py
def EMA(df, base, target, period, alpha=False):
    """
    Function to compute Exponential Moving Average (EMA)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the EMA needs to be computed from
        target : String indicates the column name to which the computed data needs to be stored
        period : Integer indicates the period of computation in terms of number of candles
        alpha : Boolean if True indicates to use the formula for computing EMA using alpha (default is False)

    Returns :
        df : Pandas DataFrame with new column added with name 'target'
    """

    con = pd.concat([df[:period][base].rolling(window=period).mean(), df[period:][base]])

    if (alpha == True):
        # (1 - alpha) * previous_val + alpha * current_val where alpha = 1 / period
        df[target] = con.ewm(alpha=1 / period, adjust=False).mean()
    else:
        # ((current_val - previous_val) * coeff) + previous_val where coeff = 2 / (period + 1)
        df[target] = con.ewm(span=period, adjust=False).mean()

    df[target].fillna(0, inplace=True)
    return df

def ATR(df, period, ohlc=['open', 'high', 'low', 'close']):
    """
    Function to compute Average True Range (ATR)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])

    Returns :
        df : Pandas DataFrame with new columns added for
            True Range (TR)
            ATR (ATR_$period)
    """
    atr = 'ATR_' + str(period)

    # Compute true range only if it is not computed and stored earlier in the df
    if not 'TR' in df.columns:
        df['h-l'] = df[ohlc[1]] - df[ohlc[2]]
        df['h-yc'] = abs(df[ohlc[1]] - df[ohlc[3]].shift())
        df['l-yc'] = abs(df[ohlc[2]] - df[ohlc[3]].shift())

        df['TR'] = df[['h-l', 'h-yc', 'l-yc']].max(axis=1)

        df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)

    # Compute EMA of true range using ATR formula after ignoring first row
    EMA(df, 'TR', atr, period, alpha=True)

    return df

def SuperTrend(df, period = supertrend_period, multiplier=supertrend_multiplier, ohlc=['open', 'high', 'low', 'close']):
    """
    Function to compute SuperTrend

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        multiplier : Integer indicates value to multiply the ATR
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])

    Returns :
        df : Pandas DataFrame with new columns added for
            True Range (TR), ATR (ATR_$period)
            SuperTrend (ST_$period_$multiplier)
            SuperTrend Direction (STX_$period_$multiplier)
    """

    ATR(df, period, ohlc=ohlc)
    atr = 'ATR_' + str(period)
    st = 'ST' #+ str(period) + '_' + str(multiplier)
    stx = 'STX' #  + str(period) + '_' + str(multiplier)

    """
    SuperTrend Algorithm :

        BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR
        BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR

        FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous Close > Previous FINAL UPPERBAND))
                            THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
        FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous Close < Previous FINAL LOWERBAND)) 
                            THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)

        SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close <= Current FINAL UPPERBAND)) THEN
                        Current FINAL UPPERBAND
                    ELSE
                        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close > Current FINAL UPPERBAND)) THEN
                            Current FINAL LOWERBAND
                        ELSE
                            IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close >= Current FINAL LOWERBAND)) THEN
                                Current FINAL LOWERBAND
                            ELSE
                                IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close < Current FINAL LOWERBAND)) THEN
                                    Current FINAL UPPERBAND
    """

    # Compute basic upper and lower bands
    df['basic_ub'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 + multiplier * df[atr]
    df['basic_lb'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 - multiplier * df[atr]

    # Compute final upper and lower bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] > df['final_ub'].iat[i - 1] else \
        df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] < df['final_lb'].iat[i - 1] else \
        df['final_lb'].iat[i - 1]

    # Set the Supertrend value
    df[st] = 0.00
    for i in range(period, len(df)):
        df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[
            i] <= df['final_ub'].iat[i] else \
            df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[i] > \
                                     df['final_ub'].iat[i] else \
                df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] >= \
                                         df['final_lb'].iat[i] else \
                    df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] < \
                                             df['final_lb'].iat[i] else 0.00

        # Mark the trend direction up/down
    df[stx] = np.where((df[st] > 0.00), np.where((df[ohlc[3]] < df[st]), 'down', 'up'), np.NaN)

    # Remove basic and final bands from the columns
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb'], inplace=True, axis=1)

    df.fillna(0, inplace=True)
    return df

def gethistoricaldata(token):
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(10)
    df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    try:
        data = kites[0].historical_data(token, startdate, enddate, interval=candlesize)
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
        #print(df)
        if not df.empty:
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df['date'] = df['date'].astype(str).str[:-6]
            df['date'] = pd.to_datetime(df['date'])
            df = SuperTrend(df)
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
            #print(histdata)
            super_trend = histdata.STX.values
            lastclose = histdata.close.values[-1]
            stoploss_buy = histdata.low.values[-3] # third last candle as stoploss
            stoploss_sell = histdata.high.values[-3] # third last candle as stoploss

            if stoploss_buy > lastclose * 0.996:
                stoploss_buy = lastclose * 0.996 # minimum stoploss as 0.4 %

            if stoploss_sell < lastclose * 1.004:
                stoploss_sell = lastclose * 1.004 # minimum stoploss as 0.4 %
            #print("lastclose",lastclose)
            #print("stoploss abs",stoploss)
            print(tickerlist[i],lastclose,super_trend[-4:])

            if super_trend[-1]=='up' and super_trend[-3]=='down' and super_trend[-4]=='down' and super_trend[-5]=='down' and super_trend[-6]=='down':
                stoploss_buy = lastclose - stoploss_buy
                #print("stoploss delta", stoploss)

                quantity = floor(max(1, (risk_per_trade/stoploss_buy)))
                target = stoploss_buy*3 # risk reward as 3

                price = int(100 * (floor(lastclose / 0.05) * 0.05)) / 100
                stoploss_buy = int(100 * (floor(stoploss_buy / 0.05) * 0.05)) / 100
                quantity = int(quantity)
                target = int(100 * (floor(target / 0.05) * 0.05)) / 100

                orderslist.append(tickerlist[i])
                order = kites[0].place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="BUY",
                                             quantity=quantity,
                                             price=price,
                                             product='MIS',
                                             order_type='LIMIT',
                                             validity='DAY',
                                             trigger_price='0',
                                             # disclosed_quantity=None,
                                             squareoff=target,
                                             stoploss=stoploss_buy,
                                             #trailing_stoploss=trailing_loss,
                                             variety="bo"
                                             )
                print("         Order : ", "BUY", tickerlist[i], "quantity:",quantity, "target:",target, "stoploss:",stoploss_buy,datetime.datetime.now())

            if super_trend[-1]=='down' and super_trend[-3]=='up' and super_trend[-4]=='up' and super_trend[-5]=='up' and super_trend[-6]=='up':

                stoploss_sell= stoploss_sell - lastclose
                #print("stoploss delta", stoploss)

                quantity = floor(max(1, (risk_per_trade/stoploss_sell)))
                target = stoploss_sell*3 # risk reward as 3

                price = int(100 * (floor(lastclose / 0.05) * 0.05)) / 100
                stoploss_sell = int(100 * (floor(stoploss_sell / 0.05) * 0.05)) / 100
                quantity = int(quantity)
                target = int(100 * (floor(target / 0.05) * 0.05)) / 100

                orderslist.append(tickerlist[i])
                order = kites[0].place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="SELL",
                                             quantity=quantity,
                                             price=price,
                                             product='MIS',
                                             order_type='LIMIT',
                                             validity='DAY',
                                             trigger_price='0',
                                             # disclosed_quantity=None,
                                             squareoff=target,
                                             stoploss=stoploss_sell,
                                             #trailing_stoploss=trailing_loss,
                                             variety="bo"
                                             )
                print("         Order : ", "SELL", tickerlist[i], "quantity:",quantity, "target:",target, "stoploss:",stoploss_sell,datetime.datetime.now())

        except Exception as e :
            print(e)

def run():
    global runcount
    start_time = int(9) * 60 + int(30)  # specify in int (hr) and int (min) foramte
    end_time = int(15) * 60 + int(10)  # do not place fresh order
    stop_time = int(15) * 60 + int(15)  # square off all open positions
    last_time = start_time
    schedule_interval = 180  # run at every 3 min
    #runcount = 0
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

