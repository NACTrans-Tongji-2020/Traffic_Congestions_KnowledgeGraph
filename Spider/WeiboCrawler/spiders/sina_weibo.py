# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
from datetime import datetime,timedelta
from lxml import etree
from scrapy import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from urllib.parse import quote, unquote 
from WeiboCrawler.items import TweetsItem, WeatherItem
from .utils import time_fix, extract_weibo_content, extract_comment_content

class WeiboCNSpider(Spider):
    name = "weibo-cn"
    base_url = 'https://weibo.cn/'

    def start_requests(self):
        # Define the list consists of user-ids of interests (uoi)
        uoi = ['2901636020']
        for uid in uoi:
            yield Request("https://weibo.cn/%s/profile?page=1" % uid, callback=self.parse_tweets, dont_filter=True)
    
    def parse_tweets(self, response):
        """ Get tweets from specific pages. """
        if response.url.endswith('page=1'):
            # If it's the first page, recursively get contents from other pages first.
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = int(all_page.group(1))
                self.log("Total page: {}".format(all_page))
                for page in range(2, all_page+1):
                    page_url = response.url.replace('page=1','page={}'.format(page))
                    yield Request(page_url, self.parse_tweets,  meta=response.meta)
        
        """ Decode and save current page data """
        tree_node = etree.HTML(response.body)
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                tweet_item = TweetsItem()
                tweet_item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                tweet_repost_url = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href')[0]
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)
                tweet_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(user_tweet_id.group(2),
                                                                           user_tweet_id.group(1))
                tweet_item['user_id'] = user_tweet_id.group(2)
                tweet_item['_id'] = '{}_{}'.format(user_tweet_id.group(2), user_tweet_id.group(1))
                create_time_info_node = tweet_node.xpath('.//span[@class="ct"]')[-1]
                create_time_info = create_time_info_node.xpath('string(.)')
                if "来自" in create_time_info:
                    tweet_item['post_time'] = time_fix(create_time_info.split('来自')[0].strip())
                    tweet_item['platform'] = create_time_info.split('来自')[1].strip()
                else:
                    tweet_item['created_at'] = time_fix(create_time_info.strip())

                like_num = tweet_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
                tweet_item['like_num'] = int(re.search('\d+', like_num).group())

                repost_num = tweet_node.xpath('.//a[contains(text(),"转发[")]/text()')[-1]
                tweet_item['repost_num'] = int(re.search('\d+', repost_num).group())

                comment_num = tweet_node.xpath(
                    './/a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()')[-1]
                tweet_item['comment_num'] = int(re.search('\d+', comment_num).group())

                images = tweet_node.xpath('.//img[@alt="图片"]/@src')
                if images:
                    tweet_item['img_url'] = [images[0] if 'http:' in images[0] else ('http:'+images[0])]

                videos = tweet_node.xpath('.//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    tweet_item['vid_url'] = [videos[0] if 'http:' in videos[0] else ('http:'+videos[0])]

                map_node = tweet_node.xpath('.//a[contains(text(),"显示地图")]')
                if map_node:
                    map_node = map_node[0]
                    map_node_url = map_node.xpath('./@href')[0]
                    map_info = re.search(r'xy=(.*?)&', map_node_url).group(1)
                    tweet_item['loc_info'] = map_info

                repost_node = tweet_node.xpath('.//a[contains(text(),"原文评论[")]/@href')
                if repost_node:
                    tweet_item['ori_weibo'] = repost_node[0]

                # Check if has read full text
                all_content_link = tweet_node.xpath('.//a[text()="全文" and contains(@href,"ckAll=1")]')
                if all_content_link:
                    all_content_url = self.base_url + all_content_link[0].xpath('./@href')[0]
                    yield Request(all_content_url, callback=self.parse_all_content, meta={'item': tweet_item},
                                  priority=1)

                else:
                    tweet_html = etree.tostring(tweet_node, encoding='unicode')
                    tweet_item['content'] = extract_weibo_content(tweet_html)
                    yield tweet_item
              
            except Exception as e:
                self.logger.error(e)
    
    def parse_all_content(self, response):
        """ Crawl down full contents """
        tree_node = etree.HTML(response.body)
        tweet_item = response.meta['item']
        content_node = tree_node.xpath('//*[@id="M_"]/div[1]')[0]
        tweet_html = etree.tostring(content_node, encoding='unicode')
        tweet_item['content'] = extract_weibo_content(tweet_html)
        yield tweet_item

class SWeiboSpider(Spider):
    name = "s-weibo"
    base_urls = 'https://s.weibo.com/'

    def getdate(self, begin, days):
        """ Get date list with begin date (format: %Y-%m-%d) and range of days. """
        fmt = '%Y-%m-%d'
        date = [(datetime.strptime(begin, fmt)+timedelta(days=i)).strftime(fmt) \
                        for i in range(days)]
        return date

    def start_requests(self):
        """ Modify keywords if needed. """
        keywords = ['路况','深圳交通管制','深圳马拉松','深圳车检']
        date_list = self.getdate('2016-12-19', 7)
        hours = range(23)
        for key in keywords:
            for date in date_list:
                for hour in hours:
                    url = 'https://s.weibo.com/weibo?q=%s&region=custom:44:3&typeall=1&suball=1&timescope=custom:%s&Refer=g&page=1'
                    timescope = '%s-%d:%s-%d' % (date,hour,date,hour+1)
                    self.keyword = key
                    yield Request(url % (quote(key),timescope), callback=self.parse_tweets, dont_filter=True)
    
    def parse_tweets(self, response):
        tree_node = etree.HTML(response.body)
        tweet_item = TweetsItem()
        """ If no results, continue. """
        if tree_node.xpath('//*[contains(@class, "no-result")]'):
            self.logger.info("Page %s has no results." % response.url)
            return tweet_item
        """ Get tweets from specific pages. """
        if response.url.endswith('page=1'):
            # If it's the first page, recursively get contents from other pages first.
            all_page_urls = tree_node.xpath('//*[@class="m-page"]/div/span/ul/li/a/@href')
            if len(all_page_urls)>1:
                for page_url in all_page_urls[1: ]:
                    yield Request('https://s.weibo.com'+ page_url, self.parse_tweets,  meta=response.meta)
        
        """ Decode and save current page data """
        tweet_nodes = tree_node.xpath('//*[@class="card"]')
        for tweet_node in tweet_nodes:
            try:
                tweet_item['key_word'] = self.keyword
                tweet_item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                tweet_url = tweet_node.xpath('.//div[@class="content"]/p[@class="from"]/a[1]/@href')[0]
                tweet_ids = re.search(r'com/(\d+)/(.*?)\?', tweet_url)
                tweet_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(tweet_ids.group(1),
                                                                           tweet_ids.group(2))
                tweet_item['user_id'] = tweet_ids.group(1)
                tweet_item['_id'] = tweet_ids.group(2)
                feed_time = tweet_node.xpath('string(.//div[@class="content"]/p[@class="from"]/a[1]/text())')
                feed_platform = tweet_node.xpath('string(.//div[@class="content"]/p[@class="from"]/a[2])')
                if feed_time and feed_platform:
                    tweet_item['post_time'] = time_fix(feed_time.strip()).replace(' ','')
                    tweet_item['platform'] = feed_platform.strip().replace(' ','')

                like_num = tweet_node.xpath('string(.//div[@class="card-act"]//li[4]//em/text())')
                if like_num:
                    tweet_item['like_num'] = int(re.search('\d+', like_num).group())
                else:
                    tweet_item['like_num'] = 0

                repost_num =  re.search('\d+',tweet_node.xpath('string(.//div[@class="card-act"]//li[2]/a/text())'))
                if repost_num:
                    tweet_item['repost_num'] = int(repost_num.group())
                else:
                    tweet_item['repost_num'] = 0

                comment_num = re.search('\d+', tweet_node.xpath('string(.//div[@class="card-act"]//li[3]/a/text())'))
                if comment_num:
                    tweet_item['comment_num'] =  int(comment_num.group())
                else:
                    tweet_item['comment_num'] = 0

                images = tweet_node.xpath('.//div[@class="content"]/div[contains(@node-type,"media")]//img[contains(@action-type,"pic")]/@src')
                if images:
                    imgs =[]
                    for img in images:
                        imgs.append(img if 'http:' in img else ('http:'+img))
                    tweet_item['img_url'] = imgs

                video = tweet_node.xpath('.//div[@class="content"]/div[contains(@node-type,"media")]//a[contains(@node-type,"video")]/@action-data')
                if video:
                    vid = unquote(re.search(r'full_url=(.*?)\&', video[0]).group(1))
                    tweet_item['vid_url'] = [vid if 'http:' in vid else ('http:'+vid)]

                repost_node = tweet_node.xpath('.//div[@class="card-comment"]//div[@class="func"]/p[@class="from"]/a[1]/@href')
                if repost_node:
                    tweet_item['ori_weibo'] = [repost_node[0] if 'http:' in repost_node[0] else ('http:'+repost_node[0])]

                # Check if has read full text
                all_content = tweet_node.xpath('.//*[@class="content"]/p[@node-type="feed_list_content_full"]')
                if all_content:
                    content_html = etree.tostring(all_content[0], encoding='unicode')
                    tweet_item['content'] = extract_weibo_content(content_html)
                    yield tweet_item

                else:
                    content_node = tweet_node.xpath('.//*[@class="content"]/p[@node-type="feed_list_content"]')
                    tweet_html = etree.tostring(content_node[0], encoding='unicode')
                    tweet_item['content'] = extract_weibo_content(tweet_html)
                    yield tweet_item

            except Exception as e:
                self.logger.error(e)

class TianqiSpider(Spider):
    name = "tianqi"
    start_urls = ['http://lishi.tianqi.com']

    def start_requests(self):
        r"""The main function to start crawling

        Params:
            city_list (list): the target citiess.
            date_list (list): the focus dates.

        Return:
            request (scrapy.Request): initialize spider.
        """
        city_list = ['shenzhen']
        date_list = ['201612']
        for city in city_list:
            for date in date_list:
                url = 'http://lishi.tianqi.com/%s/%s.html'
                yield Request(url%(city, date), callback=self.parse_tianqi, dont_filter=True)

    def parse_tianqi(self, response):
        r"""The parsing function for decoding and storing crawled data.
        
        Return:
            weather_item (scrapy.Item): Weather data
        """

        tree_node = etree.HTML(response.body)
        weather_item = WeatherItem()

        """Decode and save current page data. """
        records = tree_node.xpath('//*[@class="lishitable_content clearfix"]/li')
        for record in records:
            try:
                weather_item['_date'] = record.xpath('string(.//a/text())')
                weather_item['max_temp'] = record.xpath('string(.//div[2]/text())')
                weather_item['min_temp'] = record.xpath('string(.//div[3]/text())')
                weather_item['weather'] = record.xpath('string(.//div[4]/text())')
                weather_item['wind_dir'] = record.xpath('string(.//div[5]/text())')
                weather_item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                yield weather_item
            except Exception as e:
                self.logger.error(e)

if __name__ == "__main__":
    import os
    print(os.getcwd())
    os.system("scrapy crawl s-weibo")