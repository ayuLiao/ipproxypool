import redis
from random import choice
from config import *

redis_global = '' #全局的redis
def get_redis():
    global redis_global
    if not redis_global:
        # redis链接不存在，则重新链接
        redis_global = RedisClient()
    if not redis_global.ping():
        # redis存在，但链接失败，同样重新链接
        redis_global = RedisClient()
    return redis_global

class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD,db=DB):
        # StrictRedis中的命令与Redis完全一致
        self.rdb = redis.StrictRedis(host=host, port=port, password=password,db=db,decode_responses=True)

    #判断redis链接是否正常
    def ping(self):
        try:
            return self.rdb.get('ping')
        except:
            return False

    def add(self, proxy, score=INITIAL_SCORE):
        '''
        添加代理
        '''
        if not self.rdb.zscore(REDIS_KEY, proxy):
            return self.rdb.zadd(REDIS_KEY, score, proxy)#存入有序元组

    def random(self):
        '''
        随机获取有效代理，按分数排名获取
        :return: 随机代理
        '''
        # zrangebyscore BY 通过score来排序
        result = self.rdb.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.rdb.zrevrange(REDIS_KEY, 0 ,100)
            if len(result):
                return choice(result)
            else:
                raise RuntimeError('代理池为空')

    def decrease(self, proxy):
        '''
        代理值减一分，分数小于最小值，则代理删减
        :param proxy:
        :return: 修改后的代理分数
        '''
        score = self.rdb.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数',score,'减1')
            # ?
            return self.rdb.zincrby(REDIS_KEY, proxy ,-1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.rdb.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        '''
        判断是否存在
        :param proxy:
        :return:
        '''
        return not self.rdb.zscore(REDIS_KEY, proxy) == None

    def max(self, proxy):
        '''
        将代理设置为MAX_SCORE
        :param proxy:
        :return: 设置结果
        '''
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        return self.rdb.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def count(self):
        '''
        获得代理数量
        :return:
        '''
        return self.rdb.zcard(REDIS_KEY)

    def all(self):
        '''
        获取全部代理
        :return:
        '''
        return self.rdb.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    def batch(self, start,stop):
        '''
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        '''
        return self.rdb.zrevrange(REDIS_KEY, start, stop-1)

    # -------------爬虫方面名相关-------------

    # 爬虫方法入库
    def addcrawler(self,cralerfunc,score=INITIAL_SOCRE_CRAWLER):
        return self.rdb.zadd(CRAWLER_KEY, score, cralerfunc)  #存入有序元组

    def decreasecrawler(self, cralerfunc):
        '''
        代理值减一分，分数小于最小值，则代理删减
        :param proxy:
        :return: 修改后的代理分数
        '''
        score = self.rdb.zscore(CRAWLER_KEY, cralerfunc)
        if score and score > MIN_SCORE:
            print('爬虫方法', cralerfunc, '当前分数',score,'减1')
            # Zincrby 命令对有序集合中指定成员的分数加上增量 increment
            return self.rdb.zincrby(CRAWLER_KEY, cralerfunc ,-1)
        else:
            print('爬虫方法', cralerfunc, '当前分数', score, '移除')
            return self.rdb.zrem(CRAWLER_KEY, cralerfunc)

    def maxcrawler(self, crawlerfunc):
        '''
        将代理设置为MAX_SCORE
        :param proxy:
        :return: 设置结果
        '''
        print('方法', crawlerfunc, '可用，设置为', MAX_SOCRE_CRAWLER)
        return self.rdb.zadd(CRAWLER_KEY, MAX_SOCRE_CRAWLER, crawlerfunc)