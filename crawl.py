import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

parser = argparse.ArgumentParser()
parser.add_argument("-l","--link",action="store",type=str,dest="link",help="link of coinmarketcap whitelist")
parser.add_argument("-t","--type",action="store",type=str,dest="cointype",help="web3 or p2e")
args = parser.parse_args()

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('daring.json', scope)
client = gspread.authorize(creds)
sheet = client.open('AT가격비교의 사본')

if args.cointype == "p2e":
    sheet_instance = sheet.get_worksheet(0)
elif args.cointype == "web3":
    sheet_instance = sheet.get_worksheet(1)

headless_options = webdriver.ChromeOptions()
headless_options.add_argument('headless')
headless_options.add_argument('window-size=1920x1080')
headless_options.add_argument('disable-gpu')
headless_options.add_argument('User-Agent: Mozilla/5.0 (Macintosh: Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36')
headless_options.add_argument('lang=ko_KR')

chromedriver = 'chromedriver_win32/chromedriver'
# driver = webdriver.Chrome(chromedriver, options=headless_options)
driver = webdriver.Chrome(chromedriver)

# driver.get('https://coinmarketcap.com/ko/watchlist/619f289a89d9f82effacf1bf')
# driver.get('https://coinmarketcap.com/ko/watchlist/619f2861010b884191f6d083')
driver.get(args.link)

print(driver.title)
print(driver.current_url)

for _ in range(5):
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    time.sleep(0.5)

coins = driver.find_elements_by_class_name("iworPT")
symbols = driver.find_elements_by_class_name("coin-item-symbol")
# prices = driver.find_elements_by_class_name("sc-131di3y-0")
links = driver.find_elements_by_css_selector("div.escjiH a.cmc-link")
linksarray = []

for l in links:
    linksarray.append(l)
print("화이트리스트의 코인 개수 : ",len(coins))

result = {}
total_result = []

for l,num in zip(linksarray,range(len(coins))):
    print("COUNTER --- ",num+1)
    script = 'window.open("'+l.get_attribute('href')+'");'
    driver.execute_script(script)
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(0.5)
    btn = driver.find_elements_by_class_name("dDXPcp")
    webdriver.ActionChains(driver).click(btn[1]).perform()
    time.sleep(0.5)
    try:
        price = driver.find_element_by_css_selector("#__next > div > div > div.sc-57oli2-0.comDeo.cmc-body-wrapper > div > div.sc-16r8icm-0.eMxKgr.container > div.n78udj-0.jskEGI > div > div.sc-16r8icm-0.kjciSH.priceSection > div.sc-16r8icm-0.kjciSH.priceTitle > div > span").text
    except:
        price = driver.find_element_by_css_selector("#__next > div > div > div.sc-57oli2-0.comDeo.cmc-body-wrapper > div > div.sc-16r8icm-0.jKrmxw.container > div > div.sc-16r8icm-0.sc-19zk94m-1.gRSJaB > div.sc-16r8icm-0.iutcov > div.sc-16r8icm-0.hgKnTV > div > div:nth-child(2) > table > tbody > tr:nth-child(1) > td").text
    try:
        ath = driver.find_element_by_css_selector("#__next > div > div > div.sc-57oli2-0.comDeo.cmc-body-wrapper > div > div.sc-16r8icm-0.jKrmxw.container > div > div > div.sc-16r8icm-0.iutcov > div.sc-16r8icm-0.hgKnTV > div > div.sc-16r8icm-0.kjciSH.show > div:nth-child(2) > table > tbody > tr:nth-child(5) > td > span").text
    except:
        ath = 0
    try:
        atl = driver.find_element_by_css_selector("#__next > div > div > div.sc-57oli2-0.comDeo.cmc-body-wrapper > div > div.sc-16r8icm-0.jKrmxw.container > div > div > div.sc-16r8icm-0.iutcov > div.sc-16r8icm-0.hgKnTV > div > div.sc-16r8icm-0.kjciSH.show > div:nth-child(2) > table > tbody > tr:nth-child(6) > td > span").text
    except:
        atl = 0
    try:
        cap = driver.find_element_by_css_selector("#__next > div > div > div.sc-57oli2-0.comDeo.cmc-body-wrapper > div > div.sc-16r8icm-0.jKrmxw.container > div > div > div.sc-16r8icm-0.iutcov > div.sc-16r8icm-0.hgKnTV > div > div:nth-child(3) > table > tbody > tr:nth-child(1) > td > span").text
    except:
        cap = 0
    driver.close()
    time.sleep(0.5)
    driver.switch_to.window(driver.window_handles[0])
    result = {coins[num].text:symbols[num].text,'price':price,'ath':ath,'atl':atl,'cap':cap}
    total_result.append(result)

print("크롤링 완료! 잠시만 기다려주세요...")

coins = []
prices = []
aths = []
atls = []
caps = []
for i in total_result:
    for (k,v),num in zip(i.items(),range(len(i))):
        if num == 0:
            coins.append(k)
        if num == 1:
            prices.append(v)
        if num == 2:
            aths.append(v)
        if num == 3:
            atls.append(v)
        if num == 4:
            caps.append(v)

coins = pd.DataFrame(coins)
prices = pd.DataFrame(prices)
aths = pd.DataFrame(aths)
atls = pd.DataFrame(atls)
caps = pd.DataFrame(caps)

sheet_instance.update("A3:A50",coins.values.tolist())
sheet_instance.update("B3:B50",prices.values.tolist())
sheet_instance.update("C3:C50",aths.values.tolist())
sheet_instance.update("D3:D50",atls.values.tolist())
sheet_instance.update("G3:G50",caps.values.tolist())

print("스프레드시트 업데이트 완료")