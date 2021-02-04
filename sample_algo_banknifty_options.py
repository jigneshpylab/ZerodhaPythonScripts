import numpy as np
import sys
import pandas as pd
import time
import datetime
import pickle

quantity = 25
strike = 35000
option_type = "CE"
scantime = 5 #second

#You need to manually login and save your kite object to disc as kitetoken.pkl
try:
    with open('kitetoken.pkl', 'rb') as input:
        kite = pickle.load(input)
        print(kite.profile())
except Exception as e:
    print("ERROR in kite token")
    sys.exit()

df_inst = pd.read_csv("https://api.kite.trade/instruments")
def get_trading_symbol():
    df = df_inst[df_inst['segment'] == "NFO-OPT"]
    df = df[df['tradingsymbol'].str.startswith("{}".format("BANKNIFTY"))]
    df['expiry'] = pd.to_datetime(df['expiry'])
    expirylist = list(set(df[['tradingsymbol', 'expiry']].sort_values(by=['expiry'])['expiry'].values))
    expirylist = np.array([np.datetime64(x, 'D') for x in expirylist])
    expirylist = np.sort(expirylist)
    today = np.datetime64('today', 'D') + np.timedelta64(0,'D')
    expirylist = expirylist[expirylist >= today]
    expiry_index = 0
    next_expiry = expirylist[expiry_index]
    print("Selected expiry :", next_expiry)
    df = df[(df['expiry'] == next_expiry)]
    RHATM = int((round((strike) / 100) * 100))
    tradingsymbol = df[df['strike'] == RHATM]
    tradingsymbol = tradingsymbol[tradingsymbol['instrument_type'] == option_type]
    instrument_token = tradingsymbol.instrument_token.values[0]
    tradingsymbol = tradingsymbol.tradingsymbol.values[0]
    return tradingsymbol,instrument_token

tradingsymbol,instrument_token  = get_trading_symbol()
print("tradingsymbol",tradingsymbol)

def get_RSI(df, base="close", period=14):
    delta = df[base].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    rUp = up.ewm(com=period - 1, adjust=False).mean()
    rDown = down.ewm(com=period - 1, adjust=False).mean().abs()
    df['RSI'] = 100 - 100 / (1 + rUp / rDown)
    df['RSI'].fillna(0, inplace=True)
    return df.RSI.values[-1]

def get_historicaldata(token=instrument_token):
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(15)
    df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    try :
        data = kite.historical_data(token, startdate, enddate, interval='minute')
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
        if not df.empty:
                df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                df['date'] = df['date'].astype(str).str[:-6]
        else:
                print("Error in getting historical data")
    except Exception as e:
        print("Error in getting historical data",e)
    return df

def place_order(tradingsymbol,transaction_type,quantity,product='MIS'):
        print("New_order : {},{},{}.......{}".format(transaction_type,quantity,tradingsymbol, datetime.datetime.now()))
        quantity = int(quantity)
        ret = 0
        try:
            order_id = kite.place_order(exchange='NFO',tradingsymbol=tradingsymbol,transaction_type=transaction_type,
                                        quantity=quantity,product=product,order_type='MARKET',validity='DAY',
                                        trigger_price='0',variety="regular")
            ret = order_id
        except Exception as e:
            print(e)
        return ret

order_placed = False
def run():
    order_placed = False
    while not order_placed:
        if order_placed == True:
            break
        df = get_historicaldata()
        rsi = get_RSI(df)
        rsi_cond = False
        if rsi > 50 :
            rsi_cond = True
        ohlc_dict = kite.quote(['NFO:{}'.format(tradingsymbol)])['NFO:{}'.format(tradingsymbol)]
        vwap = ohlc_dict['average_price']
        last_price = ohlc_dict['last_price']
        vwap_cond = False
        if  last_price > vwap:
            vwap_cond = True
        cond_xyz = True
        print("\n",tradingsymbol,"RSI {:.2f} {}  ,".format(rsi,rsi_cond),"last_price {:.2f}  ,".format(last_price),
              "vwap {:.2f} {}".format(vwap,vwap_cond), datetime.datetime.now())
        if all([rsi_cond,vwap_cond,cond_xyz]):
            order_placed = True
            place_order(tradingsymbol=tradingsymbol, transaction_type="BUY", quantity=quantity,product='MIS')
        time.sleep(scantime)
run()