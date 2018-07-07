import time
from multiprocessing import Process

from Getter import Getter
from Checker import Checker
from ProxyCrawler import Crawler
from RedisClient import RedisClient
from api import app
from config import *
from logger import *

class Scheduler(object):
    def schedule_checker(self, cycle=CHECK_CYCLE):
        '''
        定时测试代理
        :param cycle: 定时周期
        :return: None
        '''
        checker = Checker()
        while True:
            log_action('代理测试器开始运行')
            checker.run()
            time.sleep(cycle)

    def schedule_getter(self, cycle=GETTER_CYCLE):
        '''
        定时获取代理
        :param cycle: 定时周期
        :return:
        '''
        getter = Getter()
        while True:
            log_action('开始抓取代理')
            getter.run()
            time.sleep(cycle)

    def schedule_api(self):
        '''
        开启web api
        :return:
        '''
        app.run(API_HOST, API_PORT)

    def run(self):
        print('代理池开始运行')
        # 判断是否开启，每个子程序都放入到一个进程中运行
        if CHECK_ENABLED:
            checker_process = Process(target=self.schedule_checker)
            checker_process.start() #放进线程中运行

        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()

        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()



