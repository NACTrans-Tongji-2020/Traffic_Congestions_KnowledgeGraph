# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import csv
import pymongo
from pymongo.errors import DuplicateKeyError
import os
import time
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from WeiboCrawler.items import TweetsItem
from WeiboCrawler.settings import LOCAL_HOST, LOCAL_PORT, DB_NAME

class WeiboJsonPipeline(object):
    def __init__(self):
        self.count = 0
        root_path = os.path.dirname(os.path.realpath(__file__))
        db_path = root_path + "\\data\\tweets.json"
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
        db_path = root_path + "\\data\\tweets.csv"
        self.db = open(db_path,'w+')
        self.writer = csv.writer(self.db)
        
    def process_item(self, item, spider):
        if item['_id']:
            self.writer.writerow((
                item['_id'],
                item['weibo_url'],
                item['post_time'],
                item['like_num'],
                item['repost_num'],
                item['comment_num'],
                item['content'].encode('utf8','ignore'),
                item['user_id'],
                item['platform'].encode('utf8','ignore'),
                item['img_url'],
                item['vid_url'],
                item['ori_weibo'],
                item['loc_info'],
                item['crawl_time'],
                item['key_word'].encode('utf8','ignore')
            ))
            self.count += 1
            return item
        else:
            raise DropItem("Invalid record")

    def open_spider(self, spider):
        self.db.close()
        print("***************Crawler {} initiated***************".format(spider.name))

    def close_spider(self, spider):
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