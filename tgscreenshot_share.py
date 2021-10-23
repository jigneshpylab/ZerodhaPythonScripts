from selenium import webdriver
import time
import telegram
import io
from PIL import Image
import datetime

bot_token = 'your bot token'
chat_id = -000000
bot = telegram.Bot(token=bot_token)


def get_screenshot(userid, passwd, pin, scrollby):
    driverpath = "C:\\chromedrive\\chromedriver.exe" #TODO set path of chromedriver
    options = webdriver.ChromeOptions()
    from io import BytesIO
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(executable_path=driverpath, chrome_options=options)
    driver.set_window_size(1920, 1080)

    driver.get('https://kite.zerodha.com/positions')

    time.sleep(5)

    username = driver.find_element_by_css_selector('input[type=text]')
    password = driver.find_element_by_css_selector('input[type=password]')

    try:
        username.send_keys(userid)
    except Exception as e:
        print(e)
    try:
        password.send_keys(passwd)
    except Exception as e:
        print(e)

    try:
        driver.find_element_by_css_selector('button[type=submit]').click()
        time.sleep(2)
    except Exception as e:
        print(e)
    time.sleep(5)

    try:
        password = driver.find_element_by_css_selector('input[type=password]')
        password.send_keys(pin)
        time.sleep(1)
        driver.find_element_by_css_selector('button[type=submit]').click()

    except Exception as e:
        print(e)

    time.sleep(3)
    try :
        if scrollby == 600 :
            driver.execute_script("scrollBy(0,600);")
        else:
            driver.execute_script("scrollBy(0,25000);")

    except Exception as e :
        print(e)
    time.sleep(3)

    path = "C:\\db\\livetradedata\\screenshot\\screenshot.png" # TODO set path to save screetshot on drive
    path2 = "C:\\db\\livetradedata\\screenshot\\{}.png".format(datetime.datetime.today().strftime("%Y%m%d%H%M%S"))

    driver.save_screenshot(path)
    driver.save_screenshot(path2)
    bio = BytesIO()
    image = Image.open(path, mode='r')
    width, height = image.size

    image = image.crop((0, 50, width, height))

    image = image.convert('RGB')

    bio.name = 'image.jpeg'
    image.save(bio, 'JPEG')
    bio.seek(0)
    bot.send_photo(chat_id, photo=bio, caption="{}".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))

    time.sleep(10)
    driver.quit()

get_screenshot("Userid","Password",000000, 600) # zerodha userid password and pin
get_screenshot("Userid","Password",000000, 0)  # zerodha userid password and pin



