# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import logging
import re
import redis
import sys
import time

from random import uniform
from scrapy.exceptions import DropItem
from scrapy.utils.log import StreamLogger
from spider.items import F5Item,IBMGuardiumItem,NBUItem

#定义全局redis连接对象
redis_client=redis.StrictRedis(host="localhost",port=6379,db=0)

def print_in_log(config_file,logger_name):
    """
    将屏幕打印输出到指定日志中
    :param  config_file
            log配置文件路径
    :type   config_file string
    
    :param  logger_name
            自定义logger名称
    :type   logger_name string
    
    :return custom_logger 自定义log对象
    """
    logging.config.fileConfig(config_file)
    custom_logger = logging.getLogger(logger_name)
    sys.stdout = StreamLogger(custom_logger,log_level=logging.INFO)
    return custom_logger

def get_item_from_redispipeline(redis_client,spider_name):
    """
    从指定redispipeline中获取item
    
    :param  spider_name
            爬虫名
    :type   spdier_name string
    
    :return item生成器
    """
    while redis_client.llen(spider_name+":items")!=0:
        yield redis_client.lpop(spider_name+":items")
        time.sleep(uniform(0,2))
     

class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item

class AngleGuard_Cleaner(object):
    """
    AngleGuard pipeline:数据清理
    清理html标签以及多余空白内容
    """
    
    
    def process_item(self,item,spider):
        if spider.name=="AngleGuard2016":
            #将屏幕打印也输出到日志中
            print_in_log("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf","AG2016")
            if item["_eventPID"]!=u'':
                for key in item.keys():
                    if key!=u"_eventPID" and key!=u"_timestamp":
                        item[key]=item[key].lstrip() #清理前部空白
                        item[key]=item[key].rstrip() #清理后部空白
                        if key!=u"_sql":
                            item[key]=item[key].strip() #清理中间所有空白 
                    #清理html标签
                    if key==u"_resultPID":
                        pattern=re.compile(r'<a.*?>(?P<result_PID>.*?)</a>')
                        item[key]=re.match(pattern, item[key]).groupdict()["result_PID"]
                #print item
                return item
            else:
                raise DropItem("Don't have lockevent.")
        else:
            return item
        
        
class AngleGuard_Save(object):
    """
    AngleGuard pipeline:存储数据
    将阻塞事件(unicode字符串)编码为utf-8,并将其保存到数据库中
    """ 
    
    
    def process_item(self,item,spider):    
        if spider.name=="AngleGuard2016":
            #将屏幕打印也输出到日志中
            custom_logger=print_in_log("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf","AG2016")
            item["_eventPID"]=item["_eventPID"].encode("utf-8")
            item["_resultPID"]=item["_resultPID"].encode("utf-8")
            item["_hostname"]=item["_hostname"].encode("utf-8")
            item["_sql"]=item["_sql"].encode("utf-8")
            time.sleep(uniform(0,2))
            item.save()
            custom_logger.info(u"事件:%s已保存进数据库" %(item["_eventPID"]))
            raise DropItem("Drop the AGitem")
        return item

class F5_Cleaner(object):
    """
    F5 pipeline:数据清理
    清理多余内容以及提取主要字段
    """
    
    def process_item(self,item,spider):
        if spider.name=="F5":
            #将屏幕打印也输出到日志中
            print_in_log("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf","F5")
            #提取成员状态图标颜色
            pattern=re.compile(r'_.*?_(?P<poolMember_Img>.*?).gif',re.S)
            item["_poolMember_Img"]=re.search(pattern,item["_poolMember_Img"]).groupdict()["poolMember_Img"]
            #清理成员状态字段多余内容     
            pattern=re.compile(r'\((?P<poolMember_status>.*?)\)',re.S)
            item["_poolMember_status"]=re.search(pattern,item["_poolMember_status"]).groupdict()["poolMember_status"]
            #print item
        return item        
        
        
class F5_Save(object):
    """
    F5 pipeline:存储数据
    将连接池信息(unicode字符串)编码为utf-8,并将其保存到数据库中
    """ 
    
    
    def process_item(self,item,spider): 
        if spider.name=="F5":
            #将屏幕打印也输出到日志中
            custom_logger=print_in_log("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf","F5")
            for json_item in get_item_from_redispipeline(redis_client,spider.name):
                redis_item=F5Item()
                json_item=json.loads(json_item)
                redis_item["_poolMember_Img"]=json_item["_poolMember_Img"].encode("utf-8")
                redis_item["_poolMember_status"]=json_item["_poolMember_status"].encode("utf-8")
                redis_item["_poolMember_name"]=json_item["_poolMember_name"].encode("utf-8")
                redis_item["_poolName"]=json_item["_poolName"].encode("utf-8")
                redis_item["_timestamp"]=json_item["_timestamp"]
                time.sleep(uniform(0,2))
                redis_item.save()
                custom_logger.info(u"Pool:%s的成员:%s已存入数据库" %(json_item["_poolName"],json_item["_poolMember_name"]))
                del redis_item
            raise DropItem("Drop the f5item")
        return item        
        

class IBM_Save(object):
    """
    IBM pipeline:存储数据
    将数据库监控信息(unicode字符串)编码为utf-8,并将其保存到数据库中
    """ 
    
    
    def process_item(self,item,spider):    
        if spider.name=="IBMGuardium":
            #将屏幕打印也输出到日志中
            custom_logger=print_in_log("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf","IBM")
            for json_item in get_item_from_redispipeline(redis_client,spider.name):
                redis_item=IBMGuardiumItem()
                json_item=json.loads(json_item)
                redis_item["_dbServer_Status"]=json_item["_dbServer_Status"].encode("utf-8")
                redis_item["_dbServertype"]=json_item["_dbServertype"].encode("utf-8")
                redis_item["_ip"]=json_item["_ip"].encode("utf-8")
                redis_item["_stap_status"]=json_item["_stap_status"].encode("utf-8")
                redis_item["_timestamp"]=json_item["_timestamp"]
                time.sleep(uniform(0,2))
                redis_item.save()
                custom_logger.info(u"DB:%s信息已存入数据库" %(json_item["_ip"]))
                del redis_item
            raise DropItem("Drop the IBMitem")
        return item 

class NBU_Save(object):
    """
    NBU pipeline:存储数据
    将备份信息(unicode字符串)编码为utf-8,并将其保存到数据库中
    """ 
    
    
    def process_item(self,item,spider):    
        if spider.name=="NBU":
            #将屏幕打印也输出到日志中
            custom_logger=print_in_log("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf","NBU")
            for json_item in get_item_from_redispipeline(redis_client,spider.name):
                redis_item=NBUItem()
                json_item=json.loads(json_item)
                redis_item["_availStorageSpace"]=item["_availStorageSpace"][0].encode("utf-8")
                redis_item["_availStorageSpaceInPercent"]=item["_availStorageSpaceInPercent"][0].encode("utf-8")
                redis_item["_usedStorageSpace"]=item["_usedStorageSpace"][0].encode("utf-8")
                redis_item["_usedStorageSpaceInPercent"]=item["_usedStorageSpaceInPercent"][0].encode("utf-8")
                redis_item["_timestamp"]=json_item["_timestamp"]
                time.sleep(uniform(0,2))
                redis_item.save()
                custom_logger.info(u"备份信息已保存进数据库")
                del redis_item
            raise DropItem("Drop the NBUitem")
        return item 







        
        
        