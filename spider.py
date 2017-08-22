#!/usr/bin/env python 
#coding: utf-8
#@author:cnboy
#@time:1101@qq.com
#@description:
import re,os,os.path
import threading
import threadpool
import urllib

import time

from logger import getlog
from sqlhand import dbhand
import  requests
import traceback
from multiprocessing.dummy import Pool as ThreadPool

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
        pass
    def getcode(self,url):
        sock=urllib.urlopen(url)

        if sock.getcode()==404 or sock.geturl()!=url:
            self.logger.error(u"网页不可访问.")
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
        Lst=WebList.keys()
        time.sleep(1)
        pool = ThreadPool(4)
        results = pool.map(self.getimgdict,Lst)
        pool.close()
        pool.join()

    def getimgdict(self,url):
        url0=url
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
        self.db.update(url0)
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
    urls=[
        # "http://www.mm131.com/xinggan/",
        # 'http://www.mm131.com/qingchun/',
        'http://www.mm131.com/xiaohua/',
        'http://www.mm131.com/chemo/',
        'http://www.mm131.com/qipao/'
    ]
    sp=spider()
    pool = threadpool.ThreadPool(10)  #建立线程池，控制线程数量为10
    reqs = threadpool.makeRequests(sp.getWebList, args_list=urls, callback=[])  #构建请求，now_time为要运行的函数，args_list为要多线程执行函数的参数，最后这个callback是可选的，是对前两个函数运行结果的操作
    [pool.putRequest(req) for req in reqs]  #多线程一块执行
    pool.wait()  #线程挂起，直到结束

def test():
    '''
     url="http://www.mm131.com/chemo/"
    sp=spider()
    sp.getWebList(url)
    '''
    sp=spider()
    sp.getimgdict("http://www.mm131.com/qingchun/1.html")
main()
# test()