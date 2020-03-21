# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import csv
import pymongo
from pymongo.errors import DuplicateKeyError
import os
import time
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.images import ImagesPipeline
from WeiboCrawler.items import TweetsItem
from WeiboCrawler.settings import LOCAL_HOST, LOCAL_PORT, DB_NAME

class WeiboJsonPipeline(object):
    def __init__(self):
        self.count = 0
        root_path = os.path.dirname(os.path.realpath(__file__))
        db_path = root_path + "\\data\\tweets-crawltime-%s.json" % time.time()
        self.db = open(db_path,'w+')
        self.init_time = time.time()
        
    def process_item(self, item, spider):
        if item['_id']:
            line = ""
            if self.count > 0 :
                line += ","
            line += json.dumps(dict(item),ensure_ascii=False) + '\n'
            self.db.write(line)
            self.count += 1
            cur = time.time()
            T = int(cur-self.init_time)
            print("Record count:{}, time:{}".format(self.count,T))
            return item
        else:
            raise DropItem("Invalid record")

    def open_spider(self, spider):
        self.db.write("[\n")
        print("***************Crawler {} initiated***************".format(spider.name))

    def close_spider(self, spider):
        self.db.write("\n]")
        print("***************Crawler {} terminated***************".format(spider.name))        

class WeiboMongoPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(LOCAL_HOST, LOCAL_PORT)
        self.db = self.client[DB_NAME]
        self.tweets = self.db['Tweets']
        
    def process_item(self, item, spider):
        try:
            self.tweets.insert(dict(item))
        except DuplicateKeyError:
           # Except duplicate keys
            raise DropItem("Duplicate record")
        return item
   
    def open_spider(self, spider):
        self.init_time = time.time()
        print("***************Crawler {} initiated***************".format(spider.name))

    def close_spider(self, spider):
        self.client.close()
        delta = time.time() - self.init_time
        print("***************Having crawled {} secs***************".format(delta))
        print("***************Crawler {} terminated***************".format(spider.name))

class WeiboCsvPipeline(object):
    def __init__(self):
        root_path = os.path.dirname(os.path.realpath(__file__))
        db_path = root_path + "\\data\\tweets-crawltime-%s.csv" % time.time()
        self.db = open(db_path,'wb')
        self.exporter = CsvItemExporter(self.db,encoding='utf-8-sig')
    
    def create_valid_csv(self, item):
        for key, value in item.items():
            if isinstance(value, str):
                if  "," in value:
                    item[key] = "\"" + value + "\""
        return item
        
    def process_item(self, item, spider):
        if item['_id']:
            item = self.create_valid_csv(item)
            self.exporter.export_item(item)
            return item
        else:
            raise DropItem("Invalid record")

    def open_spider(self, spider):
        self.exporter.start_exporting()
        print("***************Crawler {} initiated***************".format(spider.name))

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.db.close()
        print("***************Crawler {} terminated***************".format(spider.name))   

class WeiboImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        try:
            for image_url in item['img_url']:
                # Send image url to Request, download image and add param 'item' to Request.
                yield Request(image_url, meta={'item':item})
        except Exception:
            pass
    
    def file_path(self, request, response=None, info=None):
        # Get item from Request and rename folder as image post id
        item = request.meta['item']
        image_folder = item['_id']
        # Rename image file as img_url
        image_name = request.url.split('/')[-1]
        image_path = u'{0}/{1}'.format(image_folder, image_name)
        return image_path     