#食べログスクレイピング

#検索したいエリアを下記に入力
sa = "港区"

#検索したいキーワードを下記に入力
sk = "ケーキ"

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import openpyxl
import pandas as pd
import math

options = Options()
options.add_argument('--headless')
browser = webdriver.Chrome(executable_path = "./chromedriver.exe", options = options)

#読み込み待機時間設定
TIMEOUT = 10
browser.implicitly_wait(TIMEOUT)

#食べログトップページを開く
browser.get("https://tabelog.com/")

#エリア検索指定
search_area = browser.find_element_by_name("sa")

#エリア検索入力
search_area.send_keys(sa)

#キーワード検索指定
search_keyword = browser.find_element_by_name("sk")

#キーワード検索入力
search_keyword.send_keys(sk)

#検索ボタン押す
browser.find_element_by_name("form_submit").click()

#ランキング順に変更
#browser.find_element_by_class_name("navi-rstlst__label--rank").click()

#検索結果ページの情報を取得、解析
current_url = browser.current_url
res = requests.get(current_url)
soup = BeautifulSoup(res.text, "html.parser")

#検索結果の数を調べる
elems = soup.select('span[class="c-page-count__num"]')
max_count = int(elems[2].text)

#店舗別詳細ページURLを取得
max_page = math.ceil(max_count / 20)

#ページ手動設定(テスト用)
max_page = 2

page_count = 1
shop_links = []
while page_count < max_page:
    current_url = browser.current_url
    res = requests.get(current_url)
    soup = BeautifulSoup(res.text, "html.parser")
    elems = soup.select('a[class="list-rst__rst-name-target cpy-rst-name"]')
    
    for elem in elems:
        shop_links.append(elem.get("href"))
    browser.find_element_by_class_name("c-pagination__arrow--next").click()
    page_count += 1
else:
    current_url = browser.current_url
    res = requests.get(current_url)
    soup = BeautifulSoup(res.text, "html.parser")
    elems = soup.select('a[class="list-rst__rst-name-target cpy-rst-name"]')
    
    for elem in elems:
        shop_links.append(elem.get("href"))
        
    browser.quit()

#取得した店舗詳細ページへアクセスしデータを抽出しdfに格納後Excelへはきだし
tabelog_list = []
for shop_link in shop_links:
    res = requests.get(shop_link)
    soup = BeautifulSoup(res.text, "html.parser")
    shop_name = soup.find('div', class_='rstinfo-table__name-wrap').text
    shop_name = shop_name.replace('\n', "")
    #print(shop_name)
    score = soup.find('span', class_='rdheader-rating__score-val-dtl').text
    #print(score)
    #business_hours = soup.find_all('p', class_='rstinfo-table__subject')
    business_hours_list = []
    elems = soup.find_all('p', class_='rstinfo-table__subject-text')
    for elem in elems:
        if elems[-1] == elem:
            holiday = elem.text
        else:
            business_hours_list.append(elem.text)
            business_hours = ''.join(business_hours_list)
    #print(business_hours)
    #print(holiday)
    tel = soup.find('strong', class_='rstinfo-table__tel-num').text
    #print(tel)
    address = soup.find('p', class_='rstinfo-table__address').text
    #print(address)
    tabelog_list.append([shop_name, score, business_hours, holiday, tel, address])
    #print(tabelog_list)

browser.quit()

df = pd.DataFrame(tabelog_list, columns = ["店名", "評価点", "営業時間", "定休日", "電話番号", "住所"])
df.to_excel(sa + sk + "店舗情報.xlsx", index = False)