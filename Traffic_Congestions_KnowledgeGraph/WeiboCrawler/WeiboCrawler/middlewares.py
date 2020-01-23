# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from numpy.random import randint
from scrapy import signals


class WeibocrawlerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WeibocrawlerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class CookieMiddleware(object):
    """ Randomly select an account coockie for access """

    def __init__(self):
        self.account_pool = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + "/account_manager/coockie_db.csv")
    
    def process_request(self, request, spider):
        account_number = self.account_pool.loc[self.account_pool.status=='success'].shape[0]
        if account_number == 0:
            raise Exception('No available account')
        rand_index = randint(0, account_number)
        rand_account = self.account_pool.query("status=='success'").loc[rand_index].to_dict()
        request.headers.setdefault('Coockie', rand_account['coockie'])
        request.meta['account'] = rand_account


class RedirectMiddleware(object):
    """ Examine whether it's a normal response
        302/403 indicates invalid coockie/account, raise error
        418 indicates access denied """
    
    def __init__(self):
        self.account_pool = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + "/account_manager/coockie_db.csv")

    def process_response(self, request, response, spider):
        status = response.status
        if status == 302 or status == 403:
            self.account_pool.loc[self.account_pool.username==request.meta['account']['username'],\
                                    'status']='error'
            return request
        elif status == 418:
            spider.logger.error('Invalid IP access! Please change IP...')
            return request
        else:
            return response

class IPProxyMiddleware(object):
    """ Set proxy ip address """
    
    def fetch_proxy(self):
        # Rewrite this function if needed.
        # Return proxy ip as 'ip:port', e.g. '12.34.1.4:9090'
        return None
    
    def process_request(self,request,spider):
        proxy = self.fetch_proxy()
        if proxy:
            current_proxy = f'https://{proxy}'
            spider.logger.debug(f"Current Proxy IP:{current_proxy}")
            request.meta['proxy'] = current_proxy