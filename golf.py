# -*- coding: utf-8 -*-
import lxml
import sys
import lxml
import lxml.html
#import lxml.html.soupparser as soupparser
import threading
import time
import re
import urllib2, httplib
import StringIO, gzip
import pymongo
import urllib2
import urllib
import chardet
#from decode import decode
import urllib
reload(sys)
from utils import *
from ceshi import *
from get_num import *

import chardet
conn = pymongo.Connection('10.161.86.150:27017')
read_account = conn['test2']['golf2']
insert_account = conn['test2']['golf_url']
sys.setdefaultencoding("utf-8")
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"
]
def location2loc(lng,lat):
    loc = {}
    loc['type'] = 'Point'
    coordinates = []
    coordinates.append(lng)
    coordinates.append(lat)
    loc['coordinates'] = coordinates
    return loc

def main(url,city):
    isDone = False
    openTimes = 0
    while True:
        #ips = getips(1)
        #proxy = random.choice(ips)
        user_agent = random.choice(USER_AGENTS)
        headers = [{"User-Agent":user_agent},{"Accept": "text/plain","User-Agent":user_agent}][openTimes%2]
        req = urllib2.Request(url, headers=headers)
        #req.set_proxy(proxy,'http')
        print req
        try:
            page = urllib2.urlopen(req,timeout = 60)
            print "请求到了"
            #print page.info()
            page = page.read()

            try:
                try:
                    #print chardet.detect(page)
                    doc = lxml.html.fromstring(page.decode('gbk'))
                except:
                    print sys.exc_info()[0],sys.exc_info()[1]

                lens =  len(doc)
                print lens
            except:
                doc = soupparser.fromstring(page)
            isDone = True
            break
        except Exception, e:
            if openTimes>500:
                break
            openTimes += 1
            #print openTimes
    if not isDone:
        print "150次都没爬到，卧槽"
    else:
        out = {}
        a = re.findall(r'point : (.*),',page)[0]
        lat = a.split(':')[2].split('}')[0].strip()
        lat = float(lat)
        if lat > 90 or lat == 0:
            return
        print 'lat 没有问题'
        lng = a.split(':')[1].split(',')[0].strip()
        lng = float(lng)
        if 0 > lng:
            return
        print 'lng没有问题'
        loc = location2loc(lng,lat)
        print loc
        out['loc'] = loc
        out['name'] = re.findall(r"name : '(.*)',",page)[0].decode('gbk')
        out['star'] = doc.xpath('//div[@class="star_bg"]/div/@class')[0]
        out['data'] = doc.xpath('//div[@class="bc"]/table[@width="100%"]/tr/td/text()')
        out['city'] = city
        out['url'] = url
        insert_account.insert(out)
        print out
        print 'insert'
if __name__ == "__main__":
    for line in read_account.find():
        url = line['url']
        city = line['city']
        main(url,city)
        time.sleep(5)