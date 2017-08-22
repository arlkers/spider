#!/usr/bin/env python 
# -*- coding: utf-8 -*-
#@author:cnboy
#@time:1101@qq.com
#@description:
from spider import  spider
import threadpool

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