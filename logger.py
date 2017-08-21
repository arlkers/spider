#!/usr/bin/env python 
# -*- coding: utf-8 -*-
#@author:cnboy
#@time:1101@qq.com
#@description:

import logging
import  os,os.path
def getlog(info):
      logger = logging.getLogger()

      hdlr = logging.FileHandler(info['logfile'])
      formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
      hdlr.setFormatter(formatter)
      logger.addHandler(hdlr)
      try:
          logger.setLevel(info['loglevel'])
      except:
          print u"你输入的日志等级不正确"
      return logger
