# !/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
import time
from pymongo.errors import DuplicateKeyError
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from WeiboCrawler.items import TweetsItem
from WeiboCrawler.settings import LOCAL_HOST, LOCAL_PORT, DB_NAME

class WeiboCrawlerPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(LOCAL_HOST, LOCAL_PORT)
        self.db = self.client[DB_NAME]
        self.tweets = self.db['Tweets']
        
    def process_item(self, item, spider):
        try:
            self.tweets.insert(dict(item))
        except DuplicateKeyError:
           # Except duplicate keys
            pass
        return item
   
    def open_spider(self, spider):
        self.init_time = time.time()
        print("***************Crawler {} initiated***************".format(spider.name))

    def close_spider(self, spider):
        self.client.close()
        delta = time.time() - self.init_time
        print("***************Having crawled {} secs***************".format(delta))
        print("***************Crawler {} terminated***************".format(spider.name))

class WeiboImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item['img_url']:
            # Send image url to Request, download image and add param 'item' to Request.
            yield Request(image_url, meta={'item':item})
    
    def file_path(self, request, response=None, info=None):
        # Get item from Request and rename folder as image post id
        item = request.meta['item']
        image_folder = item['_id']
        # Rename image file as img_url
        image_name = request.url.split('/')[-1]
        image_path = u'{0}/{1}'.format(image_folder, image_name)
        return image_path 