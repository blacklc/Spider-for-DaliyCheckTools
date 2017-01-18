#!/usr/bin/env python
#coding:utf-8

'''
Created on 2016年12月9日

@author: lichen
'''

import logging
import re
import redis
import time
import scrapy
import sys

from scrapy.utils.log import StreamLogger
from spider.items import AngleGuardItem

class AngleGuard2016(scrapy.Spider):
    """
    定制爬虫类:爬取守护星实时阻塞事件页面信息
    """
    
    #scrapys spider属性
    name="AngleGuard2016"
    start_urls=["http://172.16.10.22/agweb/login",]
    
    base_url=None
    
    #自定义settings设置
    custom_settings={
        "DOWNLOAD_DELAY":15,
        "SCHEDULER":'scrapy.core.scheduler.Scheduler',
        "DUPEFILTER_CLASS":'scrapy.dupefilters.RFPDupeFilter'}
    
    #log设置
    logging.config.fileConfig("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf") #加载log配置文件
    custom_logger = logging.getLogger("AG2016") #获取自定义logger
    
    def cleanTbodyAndSaveEvent(self,response):
        """
        阻塞事件信息生成器。同时清理tbody中的换行符与制表符
        
        :param  tbody_context
                需要清理的tbody字符串
                
        :return event_contextList 单一阻塞事件详情列表;内容为unicode字符串
        """
        for tr_selector in response.selector.xpath('//tbody/tr'):
            event_contextList=[]
            pattern=re.compile(r'<td.*?>(?P<td_context>.*?)</td>',re.S)
            #此处调用的re方法为selector的re()方法
            for td in tr_selector.re(pattern):
                event_contextList.append(td)
            yield event_contextList   
        """
        event_contextList=[]
        pattern=re.compile(r'<tr>(?P<tr_context>.*?)</tr>',re.S)
        result_tr=re.finditer(pattern,tbody_context)
        for tr in result_tr:
            event_contextList=[]
            tbody_cleaned=tr.groupdict()["tr_context"]
            tbody_cleaned=tbody_cleaned.lstrip() #清理tbody前部空白
            tbody_cleaned=tbody_cleaned.rstrip() #清理tbody后部空白
            tbody_cleaned=tbody_cleaned.strip() #清理tbody中间所有空白
            pattern=re.compile(r'<td.*?>(?P<td_context>.*?)</td>',re.S)
            result_td=re.finditer(pattern,tbody_cleaned)
            for td in result_td:
                event_contextList.append(td.groupdict()["td_context"])
            yield event_contextList
        """
        """
        pattern=re.compile(r'<tbody>.*?<tr>(?P<tr_context>.*?)</tr>.*?</tbody>',re.S)
        result_tr=response.selector.re(pattern) #selector.re会将所有的分组都返回;
        #print result_tr
        for tr in result_tr:
            event_contextList=[]
            tbody_cleaned=tr.lstrip() #清理tbody前部空白
            tbody_cleaned=tr.rstrip() #清理tbody后部空白
            tbody_cleaned=tr.strip() #清理tbody中间所有空白 
            pattern=re.compile(r'<td.*?>(?P<td_context>.*?)</td>',re.S)
            result_td=re.finditer(pattern,tbody_cleaned)
            for td in result_td:
                event_contextList.append(td.groupdict()["td_context"])
            yield event_contextList
        """
                   
    def parse(self,response):
        """
        登陆守护星
        
        :param  response  
                请求首页返回的response
        
        :return 返回请求登陆首页的request
        """
        self.custom_logger.info(u"登陆守护星")
        #self.logger.info(u"登陆守护星")
        return scrapy.FormRequest.from_response(
                    response,
                    formdata={'loginname': 'admin', 'password': 'admin'},
                    callback=self.get_lookEventPage)
    
    def get_lookEventPage(self,response):
        """
        获取数据库实时阻塞事件页面信息
        
        :param  response  
                登陆首页后返回的response
        
        :return 返回数据库实时阻塞事件页面的request
        """
        self.custom_logger.info(u"访问实时阻塞事件页面")
        #self.logger.info(u"首次访问实时阻塞事件页面")
        #取url前缀
        pattern = re.compile(r'(.*?)(?P<base_url>.*?10\.22)(.*?)',re.S)
        self.base_url=re.match(pattern,response.url).groupdict()["base_url"]
        yield scrapy.Request(
                    url=self.base_url+"/agweb/capacity/getMakeLockInfo16.html?dbtype=112", 
                    meta={"timestamp":time.time()}, #利用request.meta在不同的页面之间传递自定义变量
                    callback=self.get_lookEvent,dont_filter=True)

    def get_lookEvent(self,response):
        """
        获取数据库实时阻塞事件
        
        :param  response
                请求数据库实时阻塞事件页面返回的response
                
        :return 返回AngleGuardItem的生成器
        """
        #print response.body
        #print response.meta
        #print response.headers
        #print response.selector
        #print response.selector.re()
        #获取当前所有阻塞事件
        self.custom_logger.info(u"开始本次爬取")
        #self.logger.info(u"开始本次爬取")
        event_number=0
        for i,lockevent in enumerate(self.cleanTbodyAndSaveEvent(response)):
            item=AngleGuardItem()
            if len(lockevent)>1:
                self.custom_logger.warning(u"爬取到数据库阻塞事件%d:" %(i+1))
                #self.logger.warning(u"爬取到数据库阻塞事件%d:" %(i+1))
                item["_timestamp"]=response.meta["timestamp"]
                item["_eventPID"]=lockevent[1]
                item["_resultPID"]=lockevent[3]
                item["_hostname"]=lockevent[5]
                item["_sql"]=lockevent[10]
                event_number=event_number+1
                yield item
        if event_number==0:
            self.custom_logger.info(u"已完成本次爬取.无阻塞事件.")
            #self.logger.info(u"已完成本次爬取.无阻塞事件.")
        else:
            self.custom_logger.info(u"已完成本次爬取.总共爬取到%d个阻塞事件." %(event_number))
            #self.logger.info(u"已完成本次爬取.总共爬取到%d个阻塞事件." %(event_number))
        yield scrapy.Request(
                    url=self.base_url+"/agweb/capacity/getMakeLockInfo16.html?dbtype=112", 
                    meta={"timestamp":time.time()},
                    callback=self.get_lookEvent,dont_filter=True) #dont_filter标志是否不进行url过滤(不使用url去重)

























