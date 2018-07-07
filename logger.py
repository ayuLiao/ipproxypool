'''
日志工具
'''
import logging
import datetime
import os

from config import LOG_PATH

logger_debug = None

logger_action = None #行为日志，记录系统中的一些行为

def init_log(level=logging.DEBUG, type='debug'):
    logger = None
    if logger:
        return
    name = datetime.datetime.today().strftime('%Y-%m-%d')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # sh = logging.StreamHandler()
    if not os.path.isdir(LOG_PATH):#文件夹不存在则创建
        os.mkdir(LOG_PATH)
    fh = logging.FileHandler(LOG_PATH+'/%s_%s.log' % (name,type))
    formatter = logging.Formatter(' %(asctime)s -%(filename)s-L%(lineno)d-%(name)s: %(message)s \n'+'-'*100)
    # sh.setFormatter(formatter)
    fh.setFormatter(formatter)
    # logger.addHandler(sh)
    logger.addHandler(fh)
    logging.debug("current log level is : %s", logging.getLevelName(logger.getEffectiveLevel()))
    if type == 'debug':
        global logger_debug
        logger_debug = logger
        return logger_debug
    elif type == 'action':
        global logger_action
        logger_action = logger
        return logger_action

# 获得logger，单例模式，保证全局只有一个logger
def _get_debug_logger():
    global logger_debug
    if not logger_debug:
        logger_debug = init_log(type='debug')
    return logger_debug

# 全局行为日志logger
def _get_action_logger():
    global logger_action
    if not logger_action:
        logger_action = init_log(type='action')
    return logger_action

def log_debug(message):
    _get_debug_logger().log(logging.DEBUG, message)


def log_action(message):
    _get_action_logger().log(logging.DEBUG, message)


if __name__ == '__main__':
    log_action('test')

