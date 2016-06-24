# coding: utf-8
__author__ = 'tuomao'
from bs4 import  BeautifulSoup
import urllib2
import gzip
import StringIO
import MySQLdb
import re
import multiprocessing

category_url={
    'books - reference':'http://apk-dl.com/apps/books-reference',
    'business':'http://apk-dl.com/apps/business',
    'comics':'http://apk-dl.com/apps/comics',
    'communication':'http://apk-dl.com/apps/communication',
    'education': 'http://apk-dl.com/apps/education',
    'entertainment': 'http://apk-dl.com/apps/entertainment',
    'finance': 'http://apk-dl.com/apps/finance',
    'health-fitness': 'http://apk-dl.com/apps/health-fitness',
    'libraries-demo': 'http://apk-dl.com/apps/libraries-demo',
    'lifestyle': 'http://apk-dl.com/apps/lifestyle',
    'media-video': 'http://apk-dl.com/apps/media-video',
    'medical': 'http://apk-dl.com/apps/medical',
    'music-audio': 'http://apk-dl.com/apps/music-audio',
    'news-magazines': 'http://apk-dl.com/apps/news-magazines',
    'personalization': 'http://apk-dl.com/apps/personalization',
    'photography': 'http://apk-dl.com/apps/photography',
    'productivity': 'http://apk-dl.com/apps/productivity',
    'shopping': 'http://apk-dl.com/apps/shopping',
    'social': 'http://apk-dl.com/apps/social',
    'tools': 'http://apk-dl.com/apps/tools',
    'transportation': 'http://apk-dl.com/apps/transportation',
    'travel-local': 'http://apk-dl.com/apps/travel-local',
    'weather': 'http://apk-dl.com/apps/weather',
    'word': 'http://apk-dl.com/apps/word'
}
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '__cfduid=d723462f94bd7bba89c61f0ec1aa62b3d1464167804; _ga=GA1.2.557160409.1464167810; __atuvc=44%7C21; __atuvs=5747f336fb6d92b8000',
    'Host': 'apk-dl.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'
}
data = None
apk_urls=[]
conn = MySQLdb.connect(host='120.27.92.166', user='root', passwd='112112', port=3306, db='apk')


def insert(url, name, developer, rate, pacname, category):
    if url[0] != 'h':
        url = 'http:'+url.strip()
    try:
        cur = conn.cursor()
        sql = "INSERT INTO apk(url, name, developer, rate, pacname, category) \
                VALUES ('%s','%s','%s','%f','%s', '%s' )" % \
              (url.encode('UTF-8'), name, developer, rate, pacname, category.encode('UTF-8'))
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()


def getdoc(url):
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    doc = response.read()
    doc = StringIO.StringIO(doc)
    gziper = gzip.GzipFile(fileobj=doc)
    return gziper.read()


def extract_apps_from_category(category, url):
    try:
        soup = BeautifulSoup(getdoc(url),"html5lib")
        apps = soup.find(attrs={'class':'items'}).find_all('a')
        for app in apps:
            tag = app.find(attrs={'class': 'price-container'})
            if tag.string.strip() == 'Free':
                url = app['href'].encode('UTF-8')
                if re.search(ur"[^\u0000-\u007F]+",url.decode('utf8')) == None:
                    rate = app.find(attrs={'class':'current-rating'})['style'][-4:-2]
                    rate = float(rate) / 20
                    if rate > 4:
                        get_apk(url, category,rate)
    except Exception as e:
        print e


def get_apk(url, category, rate):
    try:
        soup = BeautifulSoup(getdoc('http:'+url), "html5lib")
        apk_info = soup.find("div", class_="info").find_all('div')
        name = apk_info[1].contents[-1]
        pacname = apk_info[2].contents[-1]
        developer = apk_info[4].contents[2].string
        url = soup.find("a", class_="download")['href']
        soup = BeautifulSoup(getdoc('http:'+url.strip()),"html5lib")
        apk_url = soup.find_all('p')[1].find('a')['href']
        insert(apk_url, name, developer, rate, pacname, category)
    except Exception as e:
        print e


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=8)
    progress = multiprocessing.Process()
    progress.start()
    for key, value in category_url.items():
        # 分别取5页的数据
        for page in range(1,11):
            url = '%s?page=%d' % (value, page)
            print(url)
            pool.apply(extract_apps_from_category, (key, url))
    pool.close()
    progress.terminate()
    progress.join()
    pool.join()