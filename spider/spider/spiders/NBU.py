#!/usr/bin/env python
#coding:utf-8

'''
Created on 2016年12月9日

@author: lichen
'''

import logging
import json
import re
import redis
import sys
import scrapy
import time

from scrapy_redis.spiders import RedisSpider
from scrapy.utils.log import configure_logging,StreamLogger
from spider.items import NBUItem

class NBU(RedisSpider):
    """
    定制爬虫类:爬取NBU备份空间信息
    """
    
    
    #scrapys spider属性
    name="NBU"
    #start_urls=["https://172.16.10.10/appliance/SubmitLogin.action",]
    redis_key="nbu:urls" #定义保存爬虫的start_list的名称
    
    #自定义settings设置
    custom_settings={
        "DOWNLOAD_DELAY":0,
        "RETRY_TIMES":10}

    #log设置
    """
    configure_logging({
        "LOG_FILE":'/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/log/spider.log',
        "LOG_LEVEL":"DEBUG",
        'LOG_STDOUT':True,})
    """
    logging.config.fileConfig("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf") #加载log配置文件
    custom_logger = logging.getLogger("NBU") #获取自定义logger
    sys.stdout = StreamLogger(custom_logger) #将屏幕打印输出到日志中
    
    #redis对象
    redis_client=redis.StrictRedis(host="localhost",port=6379,db=0)
    
    def parse(self,response):
        """
        登陆NBU,并获取备份空间信息
        
        :param  response  
                请求首页返回的response
        :type   response  scrapy.http.Response
        
        :return 返回NBU item生成器
        """
        #清除url指纹信息
        for item in self.redis_client.sscan_iter(self.name+":dupefilter"):
            self.redis_client.srem(self.name+":dupefilter",item)
        self.custom_logger.info(u"登陆NBU,并获取备份空间信息")
        item=NBUItem()
        item["_timestamp"]=time.time()
        item["_usedStorageSpace"]=response.xpath('//span[@id="usedStorageSpaceSpanId"]/text()').extract()
        item["_usedStorageSpaceInPercent"]=response.xpath('//span[@id="usedStorageSpaceInPercentSpanId"]/text()').extract()
        item["_availStorageSpace"]=response.xpath('//span[@id="availStorageSpaceSpanId"]/text()').extract()
        item["_availStorageSpaceInPercent"]=response.xpath('//span[@id="availStorageSpaceInPercentSpanId"]/text()').extract()
        #print item
        yield item











