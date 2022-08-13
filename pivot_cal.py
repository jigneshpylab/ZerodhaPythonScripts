
def get_histdata_daily(token):
    print("...........get_histdata_daily day..........",datetime.datetime.now())

    global kite
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(15)
    df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    try:
        data = kite.historical_data(token, startdate, enddate, interval='day')
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
        if not df.empty:
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df['date'] = df['date'].astype(str).str[:-6]
            df['date'] = pd.to_datetime(df.date)
            df = df.set_index(df['date'])
    except  TokenException:
        print("Zerodha Kite TokenException")
        try:
            kite = get_kite()
            data = kite.historical_data(token, startdate, enddate, interval='minute')
            df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
            if not df.empty:
                df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                df['date'] = df['date'].astype(str).str[:-6]
                df['date'] = pd.to_datetime(df.date)
                df = df.set_index(df['date'])
        except Exception as e:
            print("Error in get_histdata_daily {}".format(e))
    return df

bndf = get_histdata_daily(token=260105) # Nifty 256265
bndf_nf = get_histdata_daily(token=256265) # Nifty 256265


pivot_available = False
pivot_available_nf = False

CLOSE = 0
if not bndf.empty:
    bndf = bndf[: yesterday]
    HIGH = bndf.high.values[-1]
    LOW = bndf.low.values[-1]
    CLOSE = bndf.close.values[-1]

    pp = (HIGH + LOW + CLOSE) / 3
    r1 = pp + pp - LOW
    s1 = pp - HIGH + pp
    r2 = pp + HIGH - LOW
    s2 = pp - HIGH + LOW

    r3 = HIGH + (2 * (pp - LOW))
    s3 = LOW - (2 * (HIGH - pp))
    pivot_available = True

CLOSE_nf = 0
if not bndf_nf.empty:
    bndf_nf = bndf_nf[: yesterday]

    HIGH_nf = bndf_nf.high.values[-1]
    LOW_nf = bndf_nf.low.values[-1]
    CLOSE_nf = bndf_nf.close.values[-1]

    pp_nf = (HIGH_nf + LOW_nf + CLOSE_nf) / 3
    r1_nf = pp_nf + pp_nf - LOW_nf
    s1_nf = pp_nf - HIGH_nf + pp_nf
    r2_nf = pp_nf + HIGH_nf - LOW_nf
    s2_nf = pp_nf - HIGH_nf + LOW_nf

    r3_nf = HIGH_nf + (2 * (pp_nf - LOW_nf))
    s3_nf = LOW_nf - (2 * (HIGH_nf - pp_nf))
    pivot_available_nf = True
