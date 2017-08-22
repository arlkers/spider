#!/usr/bin/env python 
# -*- coding: utf-8 -*-
#@author:cnboy
#@time:1101@qq.com
#@description:
from spider import spider

def test():

    # url="http://www.mm131.com/chemo/"
    # sp=spider()
    # sp.getWebList(url)

    sp=spider()
    sp.getcode('http://www.mm131.com/xiaohua/12.html')
    sp.getimgdict("http://www.mm131.com/qingchun/1.html")

test()