#!/usr/bin/env python
#coding:utf-8

'''
Created on 2016年12月9日

@author: lichen
'''

import re
import redis
import time
import logging
import scrapy
import sys

from scrapy_redis.spiders import RedisSpider
from scrapy.utils.log import StreamLogger
from spider.items import F5Item

class F5(RedisSpider):
    """
    定制爬虫类:爬取F5pool各成员状态
    """
    
    
    #scrapys spider属性
    name="F5"
    #start_urls=["https://172.16.1.102:443",]
    redis_key="f5pool:urls" #定义保存爬虫的start_list的名称
    
    #redis对象
    redis_client=redis.StrictRedis(host="localhost",port=6379,db=0)

    #配置Http Basic access authentication 
    http_user=redis_client.hget("login","f5_username")
    http_pass=redis_client.hget("login","f5_password")
    
    base_url=None
    
    #自定义settings设置
    custom_settings={"DOWNLOAD_DELAY":0,}
    
    #log设置
    logging.config.fileConfig("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf") #加载log配置文件
    custom_logger = logging.getLogger("F5") #获取自定义logger
    #sys.stdout = StreamLogger(custom_logger,log_level=logging.INFO) #将屏幕打印输出到日志中
    
    #redis对象
    redis_client=redis.StrictRedis(host="localhost",port=6379,db=0)
    
    def parse(self,response):
        """
        登陆F5 Web页面
        
        :param  response  
                请求首页返回的response
        
        :return 返回F5pool详情页面的request
        """
        #清除url指纹信息
        for item in self.redis_client.sscan_iter(self.name+":dupefilter"):
            self.redis_client.srem(self.name+":dupefilter",item)
        self.custom_logger.info(u"登陆F5页面")
        #self.logger.info(u"登陆F5页面")
        #取url前缀
        pattern = re.compile(r'(.*?)(?P<base_url>.*?443)(.*?)',re.S)
        self.base_url=re.match(pattern,response.url).groupdict()["base_url"]
        yield scrapy.Request(
                    url=self.base_url+"/tmui/Control/jspmap/tmui/locallb/pool/list.jsp?Filter=*", 
                    callback=self.get_F5PoolURL)

    def get_poolMemberName(self,tr_selector):
        """
        截取F5 Pool成员名
        
        :param  tr_selector
                各个状态成员页面行对应的selector对象
        
        :return F5 Pool成员名
        """
        return tr_selector.xpath('td/a/text()').extract()[0]
    
    def get_poolMemberStatus(self,tr_selector):
        """
        截取F5 Pool成员状态
        
        :param  tr_selector
                各个状态成员页面行对应的selector对象
        
        :return F5 Pool成员状态
        """
        return tr_selector.xpath('td[@class="last"]/text()').extract()[0]
    
    def get_poolMemberImg(self,tr_selector):
        """
        截取F5 Pool成员状态图标
        
        :param  tr_selector
                各个状态成员页面行对应的selector对象
        
        :return F5 Pool成员状态图标
        """
        return tr_selector.xpath('td[@align="center"]/img/@src').extract()[0]
    
    def get_F5PoolURL(self,response):
        """
        获取F5Pool URL
        
        :param  response
                指定pool成员状态页面response
        :type   response scrapy.http.Response
                
        :return 返回指定pool成员状态页面的request
        """
        self.custom_logger.info(u"获取所有F5Pool详细页面对应URL")
        for tr_selector in response.xpath('//a[contains(@href,"/tmui/Control/jspmap/tmui/locallb/pool/properties.jsp?name=")]/text()'):
            yield scrapy.Request(
                    url=self.base_url+"/tmui/Control/jspmap/tmui/locallb/pool/resources.jsp?name=%s&startListIndex=0&showAll=true" %(tr_selector.extract().encode("utf-8")), 
                    meta={"timestamp":time.time(),"poolname":tr_selector.extract()}, #利用request.meta在不同的页面之间传递自定义变量
                    callback=self.get_F5PoolStatus)
    
    def get_F5PoolStatus(self,response):
        """
        获取F5Pool成员状态
        
        :param  response
                指定pool成员状态页面response
                
        :return 返回F5 Item的生成器
        """
        #print response.body
        #item=F5Item()
        #提取各pool状态
        self.custom_logger.info(u"获取F5Pool成员状态")
        #self.logger.info(u"获取F5Pool成员状态")
        for tr_selector in response.xpath('//tbody/tr[contains(@class,@style)]'):
            item=F5Item()
            item["_timestamp"]=response.meta["timestamp"]
            item["_poolName"]=response.meta["poolname"]
            item["_poolMember_name"]=self.get_poolMemberName(tr_selector)
            item["_poolMember_status"]=self.get_poolMemberStatus(tr_selector)
            item["_poolMember_Img"]=self.get_poolMemberImg(tr_selector)
            yield item





















