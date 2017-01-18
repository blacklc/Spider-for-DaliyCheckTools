#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import django
import os
import scrapy
import sys

from django.core.wsgi import get_wsgi_application
from scrapy_djangoitem import DjangoItem

sys.path.append("/Users/lichen/Documents/workspace/DaliyCheck_Ver_Web/src/") #在PYTHONPATH内添加指定路径，保证之后import操作能够找到指定模块
os.environ['DJANGO_SETTINGS_MODULE'] = 'DaliyCheck_Ver_Web.settings' #指定当前django项目中的settings.py文件
application = get_wsgi_application() #获取在settings中已注册的应用

from DaliyCheck.models import lock_event,F5_PoolInfo,IBMGuardium,NBU


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AngleGuardItem(DjangoItem):
    """
    守护星Item
    """
    
    django_model=lock_event
    """
    timestamp=scrapy.Field()
    event_PID=scrapy.Field()
    result_PID=scrapy.Field()
    hostname=scrapy.Field()
    sql=scrapy.Field()
    """
    
    
class F5Item(DjangoItem):    
    """
    F5 Item
    """
    
    django_model=F5_PoolInfo
    """
    timestamp=scrapy.Field()
    poolName=scrapy.Field()
    poolMember_name=scrapy.Field()
    poolMember_status=scrapy.Field()
    poolMember_Img=scrapy.Field()
    """

class IBMGuardiumItem(DjangoItem):
    """
    IBMGuardium Item
    """
    
    django_model=IBMGuardium
    """
    timestamp=scrapy.Field()
    ip=scrapy.Field()
    dbServertype=scrapy.Field()
    stap_status=scrapy.Field()
    dbServer_Status=scrapy.Field()
    """
    
class NBUItem(DjangoItem):
    """
    NBU Item
    """
    
    django_model=NBU
    """
    timestamp=scrapy.Field()
    usedStorageSpace=scrapy.Field()
    usedStorageSpaceInPercent=scrapy.Field()
    availStorageSpace=scrapy.Field()
    availStorageSpaceInPercent=scrapy.Field()    
    """
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    