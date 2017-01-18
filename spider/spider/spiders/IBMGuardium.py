#!/usr/bin/env python
#coding:utf-8

'''
Created on 2016年12月9日

@author: lichen
'''

import json
import logging
import re
import redis
import sys
import scrapy
import time

from scrapy_redis.spiders import RedisSpider
from scrapy.utils.log import configure_logging,StreamLogger
from spider.items import IBMGuardiumItem

class IBMGuardium(RedisSpider):
    """
    定制爬虫类:爬取IBM Guardium所监控的各数据库运转状态
    """
    
    
    #scrapys spider属性
    name="IBMGuardium"
    #start_urls=["https://172.16.10.6:8443",]
    redis_key="ibmguardium:urls" #定义保存爬虫的start_list的名称
    
    base_url=None
    
    #自定义settings设置
    custom_settings={
        "DOWNLOAD_DELAY":0,
        "RETRY_TIMES":10}

    #log设置
    logging.config.fileConfig("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf") #加载log配置文件
    custom_logger = logging.getLogger("IBM") #获取自定义logger
    sys.stdout = StreamLogger(custom_logger) #将屏幕打印输出到日志中
    
    #redis对象
    redis_client=redis.StrictRedis(host="localhost",port=6379,db=0)
    
    def parse(self,response):
        """
        登陆IBM Guardium
        
        :param  response  
                请求首页返回的response
        
        :return 返回请求登陆首页的request
        """
        #清除url指纹信息
        for item in self.redis_client.sscan_iter(self.name+":dupefilter"):
            self.redis_client.srem(self.name+":dupefilter",item)
        self.custom_logger.info(u"登陆IBM Guardium")
        #self.logger.info(u"登陆IBM Guardium")
        self.custom_logger.info(u"获取登录用户名与密码")
        username=self.redis_client.hget("login","ibm_username")
        password=self.redis_client.hget("login","ibm_password")
        #del self.redis_client
        return scrapy.FormRequest.from_response(
                    response,
                    formdata={'username': username, 'password': password},
                    callback=self.get_DBStatus_frame)
    
    def get_DBStatus_frame(self,response):
        """
        获取数据库状态iframe对应请求的url
        
        :param  response  
                登陆首页后返回的response
        
        :return 返回请求数据库状态iframe的request
        """
        self.custom_logger.info(u"获取数据库状态iframe对应请求的url")
        #取crsf值
        pattern=re.compile(r'.*?jsp(.*?)"',re.S)
        crsf_string=response.xpath('//iframe[contains(@src,@frameborder)]').re(pattern)[0]
        #取url前缀
        pattern = re.compile(r'(.*?)(?P<base_url>.*?8443)(.*?)',re.S)
        self.base_url=re.match(pattern,response.url).groupdict()["base_url"]
        dbstatus_url=self.base_url+"/stapControl"+crsf_string.encode("utf-8")+'&rec={"action":"GET_STAP_SUMMARY"}'
        yield scrapy.Request(
                    url=dbstatus_url, 
                    meta={"timestamp":time.time(),"dbstatus_url":dbstatus_url}, #利用request.meta在不同的页面之间传递自定义变量
                    callback=self.get_DBStatus)
        
    def get_DBStatus(self,response):
        """
        获取数据库状态
        
        :param  response  
                登陆首页后返回的response
        
        :return 
        """
        self.custom_logger.info(u"获取数据库状态")
        if response.body:
            status_dict=json.loads(response.body)
            for db_status in status_dict[u'stapHealthSummary'][u'stapList']:
                item=IBMGuardiumItem()
                item["_timestamp"]=response.meta["timestamp"]
                item["_ip"]=db_status[u'host']
                item["_dbServertype"]=db_status[u'dbServerType']
                item["_stap_status"]=db_status[u'stapStatus']
                item["_dbServer_Status"]=db_status[u'ieStatus']
                #print item
                yield item
        else:
            self.custom_logger.warning(u"未加载数据库状态,准备重新加载数据")
            yield scrapy.Request(
                    url=response.meta["dbstatus_url"], 
                    meta={"timestamp":time.time(),"url":response.meta["dbstatus_url"]}, #利用request.meta在不同的页面之间传递自定义变量
                    callback=self.get_DBStatus,dont_filter=True)
 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    