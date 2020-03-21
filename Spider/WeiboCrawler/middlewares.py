# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from numpy.random import randint

class CookieMiddleware(object):
    """ Randomly select an account coockie for access """

    def __init__(self):
        self.db_path = os.path.dirname(os.path.abspath(__file__)) + "/account_manager/cookie_db.csv"
        self.account_pool = pd.read_csv(self.db_path)
    
    def process_request(self, request, spider):
        account_number = self.account_pool.loc[self.account_pool.status=='success'].shape[0]
        if account_number == 0:
            raise Exception('No available account')
        rand_index = randint(0, account_number)
        rand_account = self.account_pool.query("status=='success'").loc[rand_index].to_dict()
        request.headers.setdefault('Cookie', rand_account['cookie'])
        request.meta['account'] = rand_account


class RedirectMiddleware(object):
    """ Examine whether it's a normal response
        302/403 indicates invalid coockie/account, raise error
        418 indicates access denied """
    
    def __init__(self):
        self.db_path = os.path.dirname(os.path.abspath(__file__)) + "/account_manager/cookie_db.csv"
        self.account_pool = pd.read_csv(self.db_path)

    def process_response(self, request, response, spider):
        status = response.status
        if status == 302 or status == 403:
            self.account_pool.loc[self.account_pool.username==request.meta['account']['username'],\
                                    'status']='error'
            self.account_pool.to_csv(self.db_path,encoding='utf-8',index=False)
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