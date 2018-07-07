import asyncio
import aiohttp
import time
import sys
try:
    from aiohttp import ClientError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError

from RedisClient import *
from ProxyCrawler import Crawler
from config import *
from logger import *


'''
检测一个代理一般需要10多秒（服务器响应慢），所以使用aiohttp异步请求库，这样可以节省大量时间
'''

class Checker(object):
    def __init__(self):
        self.redis = get_redis()

    async def check_single_proxy(self,proxy):
        '''
        测试单个代理
        通过该代理请求网站，看其能否正常返回数据
        :param proxy: 单个代理
        :return: None
        '''
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://'+proxy
                print('正在测试',proxy)
                async with session.get(CHECK_URL,proxy=real_proxy,timeout=15,allow_redirects=False) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)# 代理可以用，则设置为100分
                        print('代理可用',proxy)
                    else:
                        self.redis.decrease(proxy) #代理不可用，代理分数减一
                        print('响应码非法', response.status, '代理', proxy)
            except (ClientError, aiohttp.client_exceptions.ClientProxyConnectionError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print('代理请求失败',proxy)


    def run(self):
        '''
        测试主函数
        :return:
        '''
        print('代理测试器开始运行')
        try:
            count = self.redis.count()
            print('当前剩余',count, '个代理')
            for i in range(0, count, BATCH_CHECK_SIZE): #100个作为一组来检查
                start = i
                stop = min(i + BATCH_CHECK_SIZE, count)
                print("正在测试第", start+1,'-', stop, '个代理')
                check_proxies = self.redis.batch(start, stop) #从redis中批量获取代理
                loop = asyncio.get_event_loop()
                tasks = [self.check_single_proxy(proxy) for proxy in check_proxies]
                loop.run_until_complete(asyncio.wait(tasks)) #异步运行，丢了100个代理进入异步任务组
                sys.stdout.flush()
                time.sleep(5)
        except Exception as e:
            print('测试器报错',e.args)
            log_debug(e.args)

