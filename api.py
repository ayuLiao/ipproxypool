from flask import Flask, g

from RedisClient import *

'''
通过Flask定义api接口，
通过api接口直接获得代理池中有效的代理
'''

app = Flask(__name__)


@app.route('/')
def index():
    return '<h2>Welcome to Proxy Pool System</h2>'

@app.route('/random')
def get_proxy():
    '''
    从redis中随机获得一个代理
    :return: 代理
    '''
    conn = get_redis()
    return conn.random()

@app.route('/count')
def get_counts():
    '''
    代理池中代理的总数
    :return: 代理总数
    '''
    conn = get_redis()
    return str(conn.count())


if __name__ == '__main__':
    app.run()