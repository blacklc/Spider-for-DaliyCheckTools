#!/usr/bin/env python
#coding:utf-8

'''
Created on 2016年12月13日

@author: lichen
'''

import os
import scrapy.cmdline  
  

if __name__ == '__main__':
    os.environ['XDG_CONFIG_HOME']='/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider'
    #os.environ['SCRAPY_SETTINGS_MODULE'] = 'spider.settings' #引入配置文件
    #scrapy.cmdline.execute(argv=['scrapy','crawl',"AngleGuard2016",]) #最后一个参数是爬虫文件名
    #scrapy.cmdline.execute(argv=['scrapy','crawl',"F5",])
    #scrapy.cmdline.execute(argv=['scrapy','crawl',"IBMGuardium",])
    #scrapy.cmdline.execute(argv=['scrapy','crawl',"NBU",])