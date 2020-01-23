# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
from lxml import etree
from scrapy import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from WeiboCrawler.items import TweetsItem
from WeiboCrawler.spiders.utils import time_fix, extract_weibo_content, extract_comment_content

class SinaWeiboSpider(Spider):
    name = "sina-weibo"
    allowed_domains = ["weibo.cn"]

    def start_requests(self):
        # Define the list consists of user-ids of interests (uoi)
        uoi = ['2901636020']
        for uid in uoi:
            yield Request(url="https://weibo.cn/%s/profile?page=1" % uid, callback=self.parse_tweets)
    
    def parse_tweets(self, response):
        """ Get tweets from specific users. """
        self.log("response: \n{}".format(response.text))
        if response.url.endswith('page=1'):
            # If it's the first page, get contents from other pages first.
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = int(all_page.group(1))
                self.log("Total page: {}".format(all_page))
                for page in range(2, all_page+1):
                    page_url = response.url.replace('page=1','page={}'.format(page))
                    yield Request(page_url, self.parse_tweets, dont_filter=True, meta=response.meta)
        
        """ Decoding current page data """
        tree_node = etree.HTML(response.body)
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                tweet_item = TweetsItem()
                tweet_item['crawl_time'] = int(time.time())
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
                    tweet_item['img_url'] = images[0]

                videos = tweet_node.xpath('.//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    tweet_item['vid_url'] = videos[0]

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

if __name__ == "__main__":
    os.chdir("H:\\ChocolateDave\\Engineering\\NACTrans2020\\Traffic_Congestions_KnowledgeGraph\\WeiboCrawler\WeiboCrawler")
    process = CrawlerProcess(get_project_settings())
    process.crawl("sina-weibo")
    process.start()