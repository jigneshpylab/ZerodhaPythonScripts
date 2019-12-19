foldername = pd.Timestamp.today().strftime('%Y%m%d')
path = 'C:\\db\\options\\{}'.format(foldername)
try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)

for instr in ["NIFTY","BANKNIFTY"] :
    try:
        print("downloading instruments tokens.....")
        df = pd.read_csv("https://api.kite.trade/instruments")
        print("instruments tokens downloded.....")
        df = df[df['segment'] == "NFO-OPT"]
        df = df[df['tradingsymbol'].str.startswith("{}".format(instr))]
        df = df[~df['tradingsymbol'].str.startswith("NIFTYIT")]
        df['expiry'] = pd.to_datetime(df['expiry'])
        tday = pd.Timestamp.today() - pd.DateOffset(5)
        print(tday)
        df = df[~(df['expiry'] <= tday)]
        df = df[df.expiry == df.expiry.min()]
        print(df)
    except Exception as e:
        print(e)
        
    tickerlist = df.tradingsymbol.values
    trade_token = df.instrument_token.values

    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(30)
    
    for i in range(0,len(trade_token)):
        df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        trade_token[i]
        try:
            data = kite.historical_data(trade_token[i], startdate, enddate, interval='minute')
            df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
            # print(df)
            if not df.empty:
                df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                df['date'] = df['date'].astype(str).str[:-6]
            else :
                print("DF EMPTY")
                # print(ticker,'\n',df,'\n\n\n')
        except Exception as e:
            print("  error in gethistoricaldata", token, e)
        # print(df)
        if not df.empty:
            df.to_csv('{}\\{}.csv'.format(path,tickerlist[i]),index=False)
        print(i,tickerlist[i])
        time.sleep(0.05)
