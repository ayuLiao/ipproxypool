from RedisClient import *
from ProxyCrawler import Crawler
from config import *


class Getter():
    def __init__(self):
        self.redis = get_redis()
        self .crawler = Crawler()

    def is_over_threshold(self):
        '''
        判断是否达到了代理池限制
        :return:
        '''
        # 判断redis数据库中有没有一万条代理数据
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        print('代理获取器开始执行')
        if not self.is_over_threshold():#超过限制就获取代理往redis里存了
            for callable_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callable_label]
                proxies = self.crawler.get_proxies(callback)# 将所有的以crawl_开头的方法都运行一遍
                for proxy in proxies:
                    self.redis.add(proxy)