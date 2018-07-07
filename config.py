
VALID_STATUS_CODES = [200] #网站正常的返回码
CHECK_URL ='http:/www.zhihu.com' #检查的网站，一般为要爬取的目标站
BATCH_CHECK_SIZE = 100


POOL_UPPER_THRESHOLD = 10000 # 代理池数量界限


MAX_SCORE = 100 #最大分数
MIN_SCORE = 0
INITIAL_SCORE = 10#初始分数
INITIAL_SOCRE_CRAWLER = 10 #爬虫方法初始化分数
MAX_SOCRE_CRAWLER = 20 #爬虫方法最大分数

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'proxies' #存代理
CRAWLER_KEY = 'crawler:func_name' #存爬虫方法名
DB = 9 #选择redis中某个数据库

# 检查周期
CHECK_CYCLE = 20
# 获取周期
GETTER_CYCLE = 300

# API配置
API_HOST = '0.0.0.0'
API_PORT = 9800

# 开关
CHECK_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = True

# 最大批测试量
BATCH_TEST_SIZE = 10

LOG_PATH = './logs'