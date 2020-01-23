# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import time
from scrapy.exceptions import DropItem
from WeiboCrawler.items import TweetsItem

class WeibocrawlerPipeline(object):
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