import schedule
import os
import time
import datetime
import socket

REMOTE_SERVER = "www.google.com"
holidays = ['28-Oct-19', '12-Nov-18', '25-Dec-18']
holidays = [datetime.datetime.strptime(i, '%d-%b-%y') for i in holidays]
holidays = [i.date() for i in holidays]

def is_connected():
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

def runalgo():
    print("Running Algo",datetime.datetime.now())
    today = datetime.datetime.today()

    if today.date() in holidays:
        print("TODAY IS HOLIDAY")
    else:
        for i in range(0, 180): # check if you are connected to internet. If not, check again after 1 min
            if is_connected():
                break
            else:
                time.sleep(60)
                continue
        try:
            os.system('C:\\pye\\trade2020\\login.py') # keep your python zerodha login script path
            time.sleep(120)
            os.system('C:\\pye\\trade2020\\algorun.py') # keep your python trading script path
        except Exception as e:
            print(e)

schedule.every().monday.at("08:35").do(runalgo)
schedule.every().tuesday.at("08:35").do(runalgo)
schedule.every().wednesday.at("08:35").do(runalgo)
schedule.every().thursday.at("08:35").do(runalgo)
schedule.every().friday.at("08:35").do(runalgo)

while True:
    print(datetime.datetime.today())
    schedule.run_pending()
    time.sleep(30)
