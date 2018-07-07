import requests
import fake_useragent

ua = fake_useragent.UserAgent()

base_headers = {
    'User-Agent': ua.random, #伪装浏览器头
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}

def get_page(url, options={}):
    '''
    抓取不同代理页面中的代理
    :param url:
    :param options:
    :return:
    '''
    headers = dict(base_headers, **options)
    try:
        response = requests.get(url, headers=headers)
        print('抓取成功',url, response.status_code)
        if response.status_code == 200:
            return response.text
    except:
        print('链接网站失败，抓取失败',url)
        return None

if __name__ == '__main__':
    url = 'http://www.xroxy.com/proxylist.php?country=CN'
    # url = 'http://www.66ip.cn/1.html'
    html = get_page(url)
    print(html)
