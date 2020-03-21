# !/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Item, Field


class TweetsItem(Item):
    r"""Contents of Weibo tweets.
    """
    _id = Field()        # Weibo id
    weibo_url = Field()  # Weibo url
    post_time = Field()  # Posted time
    like_num = Field()   # Like number
    repost_num = Field() # Repost number
    comment_num = Field() # Comments number
    created_at = Field() # Create time
    content = Field()    # Weibo contents
    user_id = Field()    # User id
    platform = Field()   # Platoform used for posting
    img_url = Field()    # Image url
    vid_url = Field()    # Video url
    ori_weibo = Field()  # Original Weibo for reposted one
    loc_info = Field()   # Location information
    crawl_time = Field() # Crawled time
    key_word = Field()   # Keyword used for searching

class WeatherItem(Item):
    r"""Contents of weather descriptions.
    """
    _date = Field()      # Record date 
    max_temp = Field()   # Maximum temperature
    min_temp = Field()   # Minimum temperature
    weather = Field()    # Weather
    wind_dir = Field()   # Wind direction
    crawl_time = Field() # Crawled time
