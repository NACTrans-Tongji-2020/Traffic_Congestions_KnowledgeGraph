# !/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Item, Field


class TweetsItem(Item):
    """ Contents of Weibo tweets """
    _id = Field()        # Weibo id
    weibo_url = Field()  # Weibo url
    post_time = Field()  # Posted time
    like_num = Field()   # Like number
    repost_num = Field() # Repost number
    comment_num = Field()# Comments number
    content = Field()    # Weibo contents
    user_id = Field()    # User id
    platform = Field()   # Platoform used for posting
    img_url = Field()    # Image url
    vid_url = Field()    # Video url
    ori_weibo = Field()  # Original Weibo for reposted one
    loc_info = Field()   # Location information
    crawl_time = Field() # Crawled time
    key_word = Field() # Keyword for search
