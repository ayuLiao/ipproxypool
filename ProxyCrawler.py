import json
from pyquery import PyQuery as pq
import re
import time

from utils import get_page
from RedisClient import *

'''
每个获取代理都以crawl_开头，扩展时，只需添加crawl_开头方法
'''

# 代理装饰器类
# class ProxyDecoreate(object):
#     def __init__(self,func):
#         self._func = func
#
#     def __call__(self, *args, **kwargs):
#         r = get_redis()
#         t1 = time.time()
#         self._func(self)
#         t2 = time.time()
#         run_time = t2-t1
#         func_name = self._func.__name__
        # if not res:
        #     # 爬虫方法获取不到网站结果
        #     r.decreasecrawler(func_name)
        # elif res and run_time > 30.0:
        #     # 爬虫方法爬取结果使用了30秒，减分
        #     r.decreasecrawler(func_name)
        # else:
        #     r.maxcrawler(func_name)

def ProxyDecoreate(func):
    def wrapper(self, *args, **kwargs):
        r = get_redis()
        t1 = time.time()
        res = func(self, *args, **kwargs)
        t2 = time.time()
        run_time = t2-t1
        func_name = func.__name__
        if not res:
            # 爬虫方法获取不到网站结果
            r.decreasecrawler(func_name)
        elif res and run_time > 30.0:
            # 爬虫方法爬取结果使用了30秒，减分
            r.decreasecrawler(func_name)
        else:
            r.maxcrawler(func_name)
        return res
    return wrapper


#代理元类
class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        # 遍历attrs，获得该类中所有的方法信息
        for k,v in attrs.items():
            if 'crawl_' in k:
                # 给类创建一个新属性，存各种爬虫方法，方便扩展，方便调用
                attrs['__CrawlFunc__'].append(k) #所有爬虫方法
                get_redis().addcrawler(k) #方法存入redis
                count += 1
        attrs['__CrawlFuncCount__'] = count #爬虫方法个数
        return type.__new__(cls, name, bases, attrs)

class Crawler(object, metaclass=ProxyMetaclass):

    # 通过不同的爬虫方法，获取代理，添加进入代理列表
    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)): #运行不同的爬虫方法，获得其返回的代理
            print('成功获取代理', proxy)
            proxies.append(proxy)
        return proxies

    @ProxyDecoreate
    def crawl_daili66(self, page_count=4):
        '''
        获取代理66，只有前3-4页的代理才有爬取的价值
        :param page_count: 页码
        :return:
        '''
        start_url = 'http://www.66ip.cn/{}.html'
        urls = [start_url.format(page) for page in range(1, page_count+1)]
        for url in urls:
            print('Crwaling',url)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])
            else:
                return None

    @ProxyDecoreate
    def crawl_proxy360(self):
        '''
        获取proxy360网站上的代理
        :return:
        '''
        start_url = 'http://www.proxy360.cn/Region/China'
        print('Crwaling', start_url)
        html = get_page(start_url)
        if html:
            doc = pq(html)
            lines = doc('div[name="list_proxy_ip"]').items()
            for line in lines:
                ip = line.find('.tbBottomLine:nth-child(1)').text()
                port = line.find('.tbBottomLine:nth-child(2)').text()
                yield ':'.join([ip, port])
        else:
            return None

    @ProxyDecoreate
    def crawl_goubanjia(self):
        '''
        获取Goubanjia
        :return:
        '''
        start_url = 'http://www.goubanjia.com/free/gngn/index.shtml'
        html = get_page(start_url)
        if html:
            doc = pq(html)
            tds = doc('td.ip').items()
            for td in tds:
                td.find('p').remove()
                yield td.text().replace(' ','')
        else:
            return None

    @ProxyDecoreate
    def crawl_ip3366free(self):
        for page in range(1, 4):
            start_url = 'http://www.ip3366.net/free/?stype=1&page={}'.format(page)
            html = get_page(start_url)
            if html:
                ip_address = re.compile('<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
                # \s * 匹配空格，起到换行作用
                re_ip_address = ip_address.findall(html)
                for address, port in re_ip_address:
                    result = address+':'+ port
                    yield result.replace(' ', '')
            else:
                return None

    @ProxyDecoreate
    def crawl_kxdaili(self):
        for i in range(1, 11):
            start_url = 'http://www.kxdaili.com/ipList/{}.html#ip'.format(i)
            html = get_page(start_url)
            if html:
                ip_address = re.compile('<tr.*?>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
                # \s* 匹配空格，起到换行作用
                re_ip_address = ip_address.findall(html)
                for address, port in re_ip_address:
                    result = address + ':' + port
                    yield result.replace(' ', '')
            else:
                return None

    @ProxyDecoreate
    def crawl_premproxy(self):
        for i in ['China-01', 'China-02', 'China-03', 'China-04', 'Taiwan-01']:
            start_url = 'https://premproxy.com/proxy-by-country/{}.htm'.format(i)
            html = get_page(start_url)
            if html:
                ip_address = re.compile('<td data-label="IP:port ">(.*?)</td>')
                re_ip_address = ip_address.findall(html)
                for address_port in re_ip_address:
                    yield address_port.replace(' ', '')
            else:
                return None

    @ProxyDecoreate
    def crawl_xroxy(self):
        for i in ['CN', 'TW']:
            start_url = 'http://www.xroxy.com/proxylist.php?country={}'.format(i)
            html = get_page(start_url)
            if html:
                ip_address1 = re.compile("title='View this Proxy details'>\s*(.*).*")
                re_ip_address1 = ip_address1.findall(html)
                ip_address2 = re.compile("title='Select proxies with port number .*'>(.*)</a>")
                re_ip_address2 = ip_address2.findall(html)
                for address, port in zip(re_ip_address1, re_ip_address2):
                    address_port = address + ':' + port
                    yield address_port.replace(' ', '')
            else:
                return None

    @ProxyDecoreate
    def crawl_kuaidaili(self):
        for i in range(1, 4):
            start_url = 'http://www.kuaidaili.com/free/inha/{}/'.format(i)
            html = get_page(start_url)
            if html:
                ip_address = re.compile('<td data-title="IP">(.*?)</td>')
                re_ip_address = ip_address.findall(html)
                port = re.compile('<td data-title="PORT">(.*?)</td>')
                re_port = port.findall(html)
                for address, port in zip(re_ip_address, re_port):
                    address_port = address + ':' + port
                    yield address_port.replace(' ', '')
            else:
                return None

    @ProxyDecoreate
    def crawl_xicidaili(self):
        for i in range(1, 3):
            start_url = 'http://www.xicidaili.com/nn/{}'.format(i)
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Cookie': '_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJWRjYzc5MmM1MTBiMDMzYTUzNTZjNzA4NjBhNWRjZjliBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUp6S2tXT3g5a0FCT01ndzlmWWZqRVJNek1WanRuUDBCbTJUN21GMTBKd3M9BjsARg%3D%3D--2a69429cb2115c6a0cc9a86e0ebe2800c0d471b3',
                'Host': 'www.xicidaili.com',
                'Referer': 'http://www.xicidaili.com/nn/3',
                'Upgrade-Insecure-Requests': '1',
            }
            html = get_page(start_url, options=headers)
            if html:
                find_trs = re.compile('<tr class.*?>(.*?)</tr>', re.S)
                trs = find_trs.findall(html)
                for tr in trs:
                    find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
                    re_ip_address = find_ip.findall(tr)
                    find_port = re.compile('<td>(\d+)</td>')
                    re_port = find_port.findall(tr)
                    for address, port in zip(re_ip_address, re_port):
                        address_port = address + ':' + port
                        yield address_port.replace(' ', '')
            else:
                return None

    @ProxyDecoreate
    def crawl_ip3366(self):
        for i in range(1, 4):
            start_url = 'http://www.ip3366.net/?stype=1&page={}'.format(i)
            html = get_page(start_url)
            if html:
                find_tr = re.compile('<tr>(.*?)</tr>', re.S)
                trs = find_tr.findall(html)
                for s in range(1, len(trs)):
                    find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
                    re_ip_address = find_ip.findall(trs[s])
                    find_port = re.compile('<td>(\d+)</td>')
                    re_port = find_port.findall(trs[s])
                    for address, port in zip(re_ip_address, re_port):
                        address_port = address + ':' + port
                        yield address_port.replace(' ', '')
            else:
                return None

    @ProxyDecoreate
    def crawl_iphai(self):
        start_url = 'http://www.iphai.com/'
        html = get_page(start_url)
        if html:
            find_tr = re.compile('<tr>(.*?)</tr>', re.S)
            trs = find_tr.findall(html)
            for s in range(1, len(trs)):
                find_ip = re.compile('<td>\s+(\d+\.\d+\.\d+\.\d+)\s+</td>', re.S)
                re_ip_address = find_ip.findall(trs[s])
                find_port = re.compile('<td>\s+(\d+)\s+</td>', re.S)
                re_port = find_port.findall(trs[s])
                for address, port in zip(re_ip_address, re_port):
                    address_port = address + ':' + port
                    yield address_port.replace(' ', '')
        else:
            return None

    @ProxyDecoreate
    def crawl_89ip(self):
        start_url = 'http://www.89ip.cn/apijk/?&tqsl=1000&sxa=&sxb=&tta=&ports=&ktip=&cf=1'
        html = get_page(start_url)
        if html:
            find_ips = re.compile('(\d+\.\d+\.\d+\.\d+:\d+)', re.S)
            ip_ports = find_ips.findall(html)
            for address_port in ip_ports:
                yield address_port
        else:
            return None

    @ProxyDecoreate
    def crawl_data5u(self):
        start_url = 'http://www.data5u.com/free/gngn/index.shtml'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'JSESSIONID=47AA0C887112A2D83EE040405F837A86',
            'Host': 'www.data5u.com',
            'Referer': 'http://www.data5u.com/free/index.shtml',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        }
        html = get_page(start_url, options=headers)
        if html:
            ip_address = re.compile('<span><li>(\d+\.\d+\.\d+\.\d+)</li>.*?<li class=\"port.*?>(\d+)</li>', re.S)
            re_ip_address = ip_address.findall(html)
            for address, port in re_ip_address:
                result = address + ':' + port
                yield result.replace(' ', '')
        else:
            return None

    # 代理接口是图片，需要做图片识别
    # @ProxyDecoreate
    # def crawl_mimvp(self):
    #     '''
    #     米扑代理
    #     :return:
    #     '''
    #     url = 'https://proxy.mimvp.com/free.php?proxy=in_hp&sort=&page={}'
    #     for i in range(1,2):
    #         html = get_page(url.format(i))
    #         if html:
    #             pass


if __name__ == '__main__':
    crawler  = Crawler()
    for i in crawler.crawl_data5u():
        print(i)

