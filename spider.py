#!/usr/bin/env python 
#coding: utf-8
#@author:cnboy
#@time:1101@qq.com
#@description:
import re,os,os.path
import urllib

from logger import getlog
from sqlhand import dbhand
import  requests
import traceback
from multiprocessing.dummy import Pool as ThreadPool
import threading
class spider:
    def __init__(self):
        self.__info={}
        self.path=os.path.join('.',"pic")
        if not os.path.exists(self.path):
          os.mkdir(self.path)
        self.__info['logfile']="pic\\err.dat"
        self.__info['loglevel']='info'
        self.logger = getlog(self.__info)
        self.db=dbhand(self.logger)
        dbfile='mm131.db'
        self.db.dbconnect(dbfile)
        self.db.init()
        self.lock=threading.Lock()
        pass
    def getcode(self,url):
        header={}
        req=requests.get(url)
        if req.status_code==404 or req.url!=url:
            self.logger.error(u"网页不可访问.")
            return None
        content=req.content.decode("gbk")
        return content
    def getImgcode(self,url):
        content=urllib.urlopen(url)
        return content.read()

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
                self.db.insert(WebList,"urls")
                WebList={}
                links=re.findall(r'<a href=(.*?) class="page-en">(.*?)</a>',page,re.S|re.M)
                if not links or links[-2][1]!=u"\u4E0B\u4E00\u9875":
                    break
                url=os.path.dirname(url)+'/'+links[-2][0].replace('\'','')
            except Exception,e:
                self.logger.error(traceback.format_exc())
                break
        webdict=self.db.geturl()
        pool = ThreadPool(10)
        results = pool.map(self.getimgdict,webdict)
        pool.close()
        pool.join()

    def getimgdict(self,url):
        text='.html'
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
                self.SaveImg(urlimg,title)
            break

        # self.lock.acquire()#取得锁
        # self.db.update(baseurl+text,1)
        # # self.lock.release()#释放锁

    def SaveImg(self,url,title):
        path=self.path+'\\'+re.sub('\(.*?\)','',title)
        if not os.path.exists(path):
            os.mkdir(path)
        file=os.path.join(path,"%s.jpg"%title)
        if os.path.exists(file):
            return
        try:
            urllib.urlretrieve(url,file)
        except Exception ,e:
            self.logger.error(traceback.format_exc())

def main():
    url=["http://www.mm131.com/xinggan/list_6_98.html"]
    sp=spider()
    pagecode=sp.getWebList(url[0])
    # print pagecode

    sp.getimgdict("http://www.mm131.com/xinggan/2424.html")

main()