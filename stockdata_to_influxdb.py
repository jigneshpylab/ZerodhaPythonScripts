from kiteconnect import KiteConnect
import datetime
import pandas as pd
import sys
import time
from influxdb import InfluxDBClient

"""
1. connect to influx database

For one time setup
Downlonad influxdb files from https://dl.influxdata.com/influxdb/releases/influxdb-1.7.10_windows_amd64.zip
extract zip file and start influxd.exe
influxd.exe should be kept running to use influxdb

db  = InfluxDBClient(host="localhost", port = 8086)
db.create_database('tickerdb')


"""




db  = InfluxDBClient(host="localhost", port = 8086)
#db.drop_database(dbname='tickerdb')
#db.create_database('tickerdb') # if running first time, remove # to create new database
db.switch_database('tickerdb')
print(db.get_list_measurements())

"""
2. zerodha login credentials
"""

userdata = pd.read_csv("C://db//loginkey//userdata.csv")
allusers = len(userdata.index.values)
kites= [None] * allusers

for i in range(0,1):
        try:
            api_key = userdata.loc[i, "api_key"]
            api_secret = userdata.loc[i, "api_secret"]
            request_token = userdata.loc[i, "request_token"]
            access_token = userdata.loc[i, "access_token"]
            public_token = userdata.loc[i, "public_token"]
            kitei = KiteConnect(api_key=api_key)
            kitei.set_access_token(access_token)
            kites[0] = kitei
        except Exception as e:
            print(" ERROR in api_key",i , e, datetime.datetime.now())
print(sys._getframe().f_lineno, "user data loaded..........", datetime.datetime.now())


"""
3. get data 
"""

tickerlist = ["ACC","ADANIENT","ADANIPORTS","ADANIPOWER","AMARAJABAT","AMBUJACEM","APOLLOHOSP","APOLLOTYRE","ASHOKLEY","ASIANPAINT","AUROPHARMA","AXISBANK","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BALKRISIND","BANKBARODA","BANKBEES","BATAINDIA","BEL","BERGEPAINT","BHARATFORG","BHARTIARTL","BHEL","BIOCON","BOSCHLTD","BPCL","BRITANNIA","CADILAHC","CANBK","CASTROLIND","CENTURYTEX","CESC","CHOLAFIN","CIPLA","COALINDIA","COLPAL","CONCOR","CUMMINSIND","DABUR","DIVISLAB","DLF","DRREDDY","EICHERMOT","EQUITAS","ESCORTS","EXIDEIND","FEDERALBNK","GAIL","GLENMARK","GMRINFRA","GODREJCP","GOLDBEES","GRASIM","HAVELLS","HCLTECH","HDFC","HDFCBANK","HEROMOTOCO","HINDALCO","HINDPETRO","HINDUNILVR","ICICIBANK","ICICIPRULI","IDFCFIRSTB","IGL","INDIGO","INFY","IOC","ITC","JINDALSTEL","JSWSTEEL","JUBLFOOD","JUSTDIAL","KOTAKBANK","L&TFH","LICHSGFIN","LIQUIDBEES","LT","LUPIN","M&M","M&MFIN","MANAPPURAM","MARICO","MARUTI","MCDOWELL-N","MFSL","MGL","MINDTREE","MOTHERSUMI","MRF","MUTHOOTFIN","NATIONALUM","NCC","NESTLEIND","NIFTYBEES","NIITTECH","NMDC","NTPC","OIL","ONGC","PAGEIND","PEL","PETRONET","PFC","PIDILITIND","PNB","POWERGRID","PVR","RAMCOCEM","RECLTD","RELIANCE","SAIL","SBIN","SHREECEM","SIEMENS","SRF","SRTRANSFIN","SUNPHARMA","SUNTV","TATACHEM","TATACONSUM","TATAELXSI","TATAMOTORS","TATAMTRDVR","TATAPOWER","TATASTEEL","TCS","TECHM","TITAN","TORNTPHARM","TORNTPOWER","TVSMOTOR","UBL","UJJIVAN","ULTRACEMCO","UPL","VEDL","VOLTAS","WIPRO","ZEEL"]
print(len(tickerlist),tickerlist)

NSEFormat = ['NSE:{}'.format(i) for i in tickerlist]
print("len(NSEFormat)", len(NSEFormat))

opentime = int(9) * 60 + int(15)
closetime = int(15) * 60 + int(30)
timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Waiting for market to open..........", datetime.datetime.now())

while timenow < opentime:
    time.sleep(0.2)
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)


print("Market opened..........", datetime.datetime.now())


def ticker_data_collector():
    keep_running = True
    runcount = 0

    while keep_running == True :
            timenow = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
            if timenow >= closetime :
                print("Market Closed.........",datetime.datetime.now())
                keep_running = False
                break

            try :
                OHLCdict = kites[0].quote(NSEFormat)
                #print(OHLCdict)
                #tickcount=0
                for key, value in OHLCdict.items():
                    #print(tickcount,key.split(":")[1])
                    #tickcount = tickcount+1
                    try:
                        tradingsymbol = key.split(":")[1]
                        instrument_token = value['instrument_token']
                        timestamp = value['timestamp']
                        last_price = value['last_price']
                        ohlc = value['ohlc']
                        open = ohlc['open']
                        high = ohlc['high']
                        low = ohlc['low']
                        close = ohlc['close']
                        volume = value['volume']

                        change = float(last_price-close)

                        change_per = 0
                        try:
                            change_per = float(100*change/close)
                        except:
                            pass

                        last_trade_time = value['last_trade_time']
                        #print(timestamp, last_trade_time, type(timestamp), timestamp.tzinfo)
                        #print(datetime.datetime.now(), datetime.datetime.now()-datetime.timedelta(minutes = 330))

                        last_trade_time = int((timestamp-last_trade_time).total_seconds())

                        json_body = [
                            {
                                "measurement": "ticker",
                                "tags": {
                                    "tradingsymbol": tradingsymbol,
                                    "instrument_token": instrument_token
                                },
                                "time": timestamp-datetime.timedelta(minutes = 330),
                                "fields": {
                                    "last_price": float(last_price),
                                    "net_change": float(change),
                                    "open": float(open),
                                    "high": float(high),
                                    "low": float(low),
                                    "close": float(close),
                                    "volume": int(volume),
                                    "change": float(change),
                                    "change_per": float(change_per),
                                    "last_trade_time": last_trade_time
                                }
                            }
                        ]
                        #print(json_body)
                        db.write_points(json_body)

                    except Exception as e:
                        print(e)
                print(runcount, datetime.datetime.now())
                time.sleep(0.5)
                runcount = runcount + 1
            except Exception as e:
                print("ERROR", e)

ticker_data_collector()
