#!/usr/bin/env python 
#coding: utf-8
#@author:cnboy
#@time:1101@qq.com
#@description:
import random
import re,os,os.path
import urllib

import time
import urllib2

from logger import getlog
from sqlhand import dbhand
import traceback
from multiprocessing.dummy import Pool as ThreadPool

class spider:
    def __init__(self):
        self.__info={}
        self.path=os.path.join('.',"pic")
        if not os.path.exists(self.path):
          os.mkdir(self.path)
        self.__info['logfile']="err.log"
        self.__info['loglevel']='info'
        self.logger = getlog(self.__info)
        self.db=dbhand(self.logger)
        dbfile='mm131.db'
        self.db.dbconnect(dbfile)
        self.db.init()
        pass


    def randHeader(self):
        head_connection = ['Keep-Alive','close']
        head_accept = ['text/html, application/xhtml+xml, */*']
        head_accept_language = ['zh-CN,fr-FR;q=0.5','en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
        head_user_agent = ['Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                           'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                           'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                           'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
                           'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11']


        header = {
            'Connection': head_connection[0],
            'Accept': head_accept[0],
            'Accept-Language': head_accept_language[1],
            'User-Agent': head_user_agent[random.randrange(0,len(head_user_agent))]
        }
        return header

    def getcode(self,url):
        header=self.randHeader()
        request=urllib2.Request(url,headers=header)
        sock=urllib2.urlopen(request)
        if sock.getcode()==404 or sock.geturl()!=url:
            self.logger.error(url+u"网页不可访问.")
            return None
        content=sock.read().decode("gbk")
        sock.close()
        return content
    def getImgcode(self,url):
        sock=urllib.urlopen(url)
        content=sock.read()
        return content

    def getWebList(self,url):
        last_link=''
        WebList={}
        while True:
            page=self.getcode(url)
            if not page:
                break
            try:
                reg=re.compile('<dd><a.*?href="(.*?)".*? alt="(.*?)"',re.S|re.M)
                result=re.findall(reg,page)
                for  item in result:
                    if re.match("http://www.mm131.com", item[0]) and item[0] not  in WebList:
                        WebList[item[0]]=item[1]
                        print item[1],item[0]
                links=re.findall(r'<a href=(.*?) class="page-en">(.*?)</a>',page,re.S|re.M)
                if not links or links[-2][1]!=u"\u4E0B\u4E00\u9875":
                    break
                url=os.path.dirname(url)+'/'+links[-2][0].replace('\'','')
            except Exception,e:
                self.logger.error(traceback.format_exc())
                break
            # finally:
            #     self.db.insert(WebList,"urls")
            #     WebList={}
        self.logger.info(url+str(len(WebList)))
        print "Done : %4d : %s"%(len(WebList),url)
        self.db.insert(WebList,"urls")
        #查询未完成的链接
        keys=url.split('/')[-2]
        done=0
        weblst=self.db.geturl(keys,done)
        if not len(weblst):
            print "%s Done."%keys
            return
        Lst=weblst.keys()
        time.sleep(1)
        pool = ThreadPool(4)
        results = pool.map(self.getimgdict,Lst)
        pool.close()
        pool.join()

    def getimgdict(self,url):
        url0=url
        text='.html'
        try:
            keys=url.split('/')[-2]
        except:
            keys=''
        baseurl=re.sub(text,'',url)
        page=self.getcode(url)
        reg='<div class="content-page"><span class="page-ch">(.*?)</span><span'
        result=re.findall(reg,page,re.M|re.S)
        result=re.findall('\d+',result[0])[0]
        last_index=int(result)
        for i in range(1,last_index+1):
            if i==1:
                pass
            else:
                url=baseurl+'_'+str(i)+text
                page=self.getcode(url)
            reg=' <div class="content-pic">.*?<img alt="(.*?)" src="(.*?)" /></a>'
            result=re.findall(reg,page,re.S|re.M)
            if result:
                title,urlimg=result[0][0],result[0][1]
                self.SaveImg(urlimg,keys,title)
            break
        self.db.update(url0)
    def SaveImg(self,url,keys,title):
        path=self.path+'\\'+keys
        if not os.path.exists(path):
            os.mkdir(path)
        path=path+'\\'+re.sub('\(.*?\)','',title)
        if not os.path.exists(path):
            os.mkdir(path)
        file=os.path.join(path,"%s.jpg"%title)
        if os.path.exists(file):
            return
        try:
            urllib.urlretrieve(url,file)
        except Exception ,e:
            self.logger.error(traceback.format_exc())


