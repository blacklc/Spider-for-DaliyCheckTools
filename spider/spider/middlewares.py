# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import redis
import sys

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from scrapy.http import HtmlResponse
from scrapy import signals
from scrapy.utils.log import StreamLogger


def print_in_log(config_file,logger_name):
    """
    将屏幕打印输出到指定日志中
    :param  config_file
            log配置文件路径
    :type   config_file string
    
    :param  logger_name
            自定义logger名称
    :type   logger_name string
    
    :return Null
    """
    logging.config.fileConfig(config_file)
    custom_logger = logging.getLogger(logger_name)
    sys.stdout = StreamLogger(custom_logger,log_level=logging.INFO)
    return custom_logger

def get_wait_data(browser,id_probe,wait_time=10):
    """
    获取异步加载数据
    
    :param  browser
            模拟浏览器对象
            
    :param  wait_time
            扫描页面时间间隔；默认为10秒内每隔500ms扫描一次页面变化
            
    :param  id_probe
            只有AJAX加载成功才会出现的异步加载数据的html_id
    
    :return Ture or False 表示是否获得异步加载数据
    """
    try:
        wait_for_ajax_element=WebDriverWait(browser,wait_time)
        #until方法需要传入一个函数方法类型参数
        wait_for_ajax_element.until(
                                    #定义匿名函数:以driver为参数，以return driver.find_element_by_id(id_probe)为函数体
                                    lambda driver:driver.find_element_by_id(id_probe).is_displayed() 
                                    )
        print "获取异步加载数据成功"
        return True
    except:
        print "获取异步加载数据失败"
        return False

class seleniumPhantomJSMiddleware(object):
    """
    自定义downloader中间件:使用selenium和PhantomJS处理request
    """
    
    
    def process_request(self,request,spider):
        """
        使用Selenium+PhantomJS处理NBU request
        """
        if spider.name=="NBU":
            custom_logger=print_in_log("/Users/lichen/Documents/workspace/Spider_DaliyCheck_Ver_Scrapy/spider/resources/Logging.conf","NBU")
            redis_client=redis.StrictRedis(host="localhost",port=6379,db=0) #建立redis对象
            custom_logger.info(u"获取登录用户名与密码")
            username=redis_client.hget("login","nbu_username")
            password=redis_client.hget("login","nbu_password")
            custom_logger.info(u"PhantomJS is starting...")
            #Selenum+PhantomJS解决方案
            #创建phantomjs浏览器模拟对象
            p_browser=webdriver.PhantomJS(executable_path="/Library/Python/2.7/site-packages/selenium/webdriver/phantomjs/phantomjs",service_args=["--ignore-ssl-errors=yes",]) #参数ignore-ssl-errors=yes代表忽视加密的ssl连接错误
            p_browser.get(request.url)
            #提交用户登陆表单
            p_browser.find_element_by_xpath('//div[@class="loginbox"]/div[@class="holder"]/div/div[@id="wwgrp_SubmitLogin_userName"]/div[@id="wwctrl_SubmitLogin_userName"]/input').clear() 
            p_browser.find_element_by_xpath('//div[@class="loginbox"]/div[@class="holder"]/div/div[@id="wwgrp_SubmitLogin_userName"]/div[@id="wwctrl_SubmitLogin_userName"]/input').send_keys(username) 
            p_browser.find_element_by_xpath('//div[@class="loginbox"]/div[@class="holder"]/div/div[@id="wwgrp_SubmitLogin_password"]/div[@id="wwctrl_SubmitLogin_password"]/input').clear()
            p_browser.find_element_by_xpath('//div[@class="loginbox"]/div[@class="holder"]/div/div[@id="wwgrp_SubmitLogin_password"]/div[@id="wwctrl_SubmitLogin_password"]/input').send_keys(password)
            p_browser.find_element_by_xpath('//div[@class="loginbox"]/div[@class="holder"]/div/input[@value="Login"]').click()
            custom_logger.info(u"已点击登陆")
            del redis_client
            if(get_wait_data(wait_time=15,browser=p_browser,id_probe='availStorageSpaceInPercentSpanId')):
                context=p_browser.page_source
                url=p_browser.current_url
                p_browser.quit()
                return HtmlResponse(url=url,body=context,encoding="utf-8")
            else:
                return request
"""
class SpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        
        #settings = crawler.settings
        #if settings['DOWNLOADER_MIDDLEWARES_BASE']:
        #    print "log is enabled!",settings['DOWNLOADER_MIDDLEWARES_BASE']
        #else:
        #    print "log is not enalbed"
        
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
"""