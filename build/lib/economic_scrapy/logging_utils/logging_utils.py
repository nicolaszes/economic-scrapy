"""
logging配置
"""

import os
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from logging.config import dictConfig

# 定义三种日志输出格式 开始
import time
from logging.handlers import TimedRotatingFileHandler

standard_format = '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]' \
                  '[%(levelname)s][%(message)s]' #其中name为getlogger指定的名字

simple_format = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'

id_simple_format = '[%(levelname)s][%(asctime)s] %(message)s'
# 定义日志输出格式 结束
# 当前位置
cur_path = os.path.dirname(os.path.realpath(__file__))
# 日志存放路径 = 当前位置/logs
log_path_base = os.path.join(os.path.dirname(cur_path), 'logs')
# 若不存在logs文件夹，自动创建
if not os.path.exists(log_path_base): os.mkdir(log_path_base)
log_path = os.path.join(log_path_base, 'info')
err_log_path = os.path.join(log_path_base, 'error')
# 若不存在info/error文件夹，自动创建
if not os.path.exists(log_path): os.mkdir(log_path)
if not os.path.exists(err_log_path): os.mkdir(err_log_path)
# 日志文件名 = 日志路径/YYYY-MM-dd.log
# log_name = os.path.join(log_path, '%s.log' % time.strftime('%Y-%m-%d'))
log_name = os.path.join(log_path, '%s.log' % 'info_log')
# err_log_name = os.path.join(err_log_path, '%s.log' % time.strftime('%Y-%m-%d'))
err_log_name = os.path.join(err_log_path, '%s.log' % 'error_log')

LOGGING_DIC = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': standard_format
        },
        'simple': {
            'format': simple_format
        },
    },
    'filters': {},
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        #打印到终端的日志
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # 打印到屏幕
            'formatter': 'simple'
        },
        #打印到文件的日志,收集info及以上的日志
        'default': {
            'level': 'INFO',
            # 'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
            # concurrent_log_handler.ConcurrentRotatingFileHandler
            # logging.handlers.TimedRotatingFileHandler
            # class=handlers.TimedRotatingFileHandler
            # level=INFO
            # formatter=formatter
            # delay=False
            # args=('logfile.log', 'H', 1, 0)
            # 如果没有使用并发的日志处理类，在多实例的情况下日志会出现缺失
            # concurrent_log_handler.ConcurrentRotatingFileHandler
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'standard',
            'filename': log_name,  # 日志文件
            # 'maxBytes': 1024*1024*5,  # 日志大小 5M
            'backupCount': 10,
            # If delay is true,
            # then file opening is deferred until the first call to emit().
            # 'args':('logfile.log', 'H', 1, 0),
            'when': 'midnight',
            'interval': 1,
            'delay': True,
            'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
        },
        #打印到文件的日志,收集error的日志
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',#cloghandler.ConcurrentRotatingFileHandler
            'formatter': 'standard',
            'filename': err_log_name,  # 日志文件
            # 'maxBytes': 1024*1024*5,  # 日志大小 5M
            # 'backupCount': 50,
            'when': 'midnight',
            'interval': 1,
            'backupCount': 10,
            'delay': True,
            'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
        },
    },
    'loggers': {
        #logging.getLogger(__name__)拿到的logger配置
        '': {
            'handlers': ['default','error', 'console'],  # 这里把上面定义的handler都加上，即log数据既写入文件又打印到屏幕
            'level': 'DEBUG',
            'propagate': True,  # 向上（更高level的logger）传递
        },
    },
}
dictConfig(LOGGING_DIC)  # 导入上面定义的logging配置


class Logs:
    @staticmethod
    def init_log_config(operator):
        dictConfig(Logs._get_log_config(operator))

    @staticmethod
    def _get_log_config(operator):
        info_log_name = os.path.join(log_path, 'info_%s.log' % operator)
        error_log_name = os.path.join(err_log_path, 'error_%s.log' % operator)
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': standard_format
                },
                'simple': {
                    'format': simple_format
                },
            },
            'filters': {},
            'handlers': {
                'null': {
                    'level': 'DEBUG',
                    'class': 'logging.NullHandler',
                },
                #打印到终端的日志
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',  # 打印到屏幕
                    'formatter': 'simple'
                },
                #打印到文件的日志,收集info及以上的日志
                'default': {
                    'level': 'INFO',
                    # 'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
                    # concurrent_log_handler.ConcurrentRotatingFileHandler
                    # logging.handlers.TimedRotatingFileHandler
                    # class=handlers.TimedRotatingFileHandler
                    # level=INFO
                    # formatter=formatter
                    # delay=False
                    # args=('logfile.log', 'H', 1, 0)
                    # 如果没有使用并发的日志处理类，在多实例的情况下日志会出现缺失
                    # concurrent_log_handler.ConcurrentRotatingFileHandler
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'formatter': 'standard',
                    'filename': info_log_name,  # 日志文件
                    # 'maxBytes': 1024*1024*5,  # 日志大小 5M
                    # 'backupCount': 50,
                    # If delay is true,
                    # then file opening is deferred until the first call to emit().
                    # 'args':('logfile.log', 'H', 1, 0),
                    'backupCount': 10,
                    'when': 'midnight',
                    'interval': 1,
                    'delay': True,
                    'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
                },
                #打印到文件的日志,收集error的日志
                'error': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.TimedRotatingFileHandler',#cloghandler.ConcurrentRotatingFileHandler
                    'formatter': 'standard',
                    'filename': error_log_name,  # 日志文件
                    # 'maxBytes': 1024*1024*5,  # 日志大小 5M
                    # 'backupCount': 50,
                    'backupCount': 10,
                    'when': 'midnight',
                    'interval': 1,
                    'delay': True,
                    'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
                },
            },
            'loggers': {
                #logging.getLogger(__name__)拿到的logger配置
                '': {
                    'handlers': ['default','error', 'console'],  # 这里把上面定义的handler都加上，即log数据既写入文件又打印到屏幕
                    'level': 'DEBUG',
                    'propagate': True,  # 向上（更高level的logger）传递
                },
            },
        }

    @staticmethod
    def get_log(name=None):
        # dictConfig(LOGGING_DIC)  # 导入上面定义的logging配置
        return logging.getLogger(name)


def multi_thread_test():
    executor = ThreadPoolExecutor(10)
    for i in range(0,10):
        executor.submit(load_my_logging_cfg,'thread_%s'%i)
    pass


def load_my_logging_cfg(thread_name):
    Logs.init_log_config("oper")
    logger = Logs.get_log(__name__) # 生成一个log实例
    for i in range(0,1000000):
        logger.info('%s,%s,It works!'%(thread_name,i))  # 记录该文件的运行状态
        logger.error('%s,%s,It works!'%(thread_name,i))

if __name__ == '__main__':
    multi_thread_test()
