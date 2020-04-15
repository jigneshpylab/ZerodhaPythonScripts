import pandas as pd
import datetime


url = "https://api.kite.trade/instruments"
df = pd.read_csv(url)   
todate=datetime.date.today().strftime('%Y.%m.%d')

df.to_csv('C:\kdb\inst\{}.csv'.format(todate))