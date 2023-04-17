import datetime
import logging
import random


def make_rand_arr(length, count, start=0) -> list:
    """
    生成随机字符串数组
    :param length: 素材的总数
    :param count: 随机的个数
    :param start: 偏移
    :return: list
    """
    arr = list()
    while len(arr) != count:
        rand = random.randint(1, length - start)
        if arr.count(rand) == 0:
            arr.append(rand)
    
    # arr.sort()
    return arr


def make_rand_str(length=6) -> str:
    """
    生成随机字符串
    :param length: 字符串长度
    :return: str
    """
    randList = random.sample('zyxwvutsrqponmlkjihgfedcba', length)
    return ''.join(randList)


def split_list(arr: list, n: int) -> list:
    """
    数组分片
    :param arr: 原始数组
    :param n: 每片长度
    :return: list
    """
    return [arr[i:i + n] for i in range(0, len(arr), n)]


def get_time() -> str:
    """获取日志"""
    return datetime.datetime.now().strftime('%Y-%m-%d')


def get_log_file_path() -> str:
    """返回日志文件目录"""
    return 'logs/' + get_time() + '.txt'


def log_error(log_path, logging_name='', console=False):
    """
    配置log
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :param console: 是否在console中输出
    :return:
    """
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出INFO及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.INFO)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    # formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s')
    formatter = logging.Formatter('[%(asctime)s] - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    if console:
        # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # 为logger对象添加句柄
        logger.addHandler(console)
    
    return logger


def get_new_date(days: int) -> list:
    """获取15天后的日期"""
    now = datetime.datetime.now()
    after = now + datetime.timedelta(days=days)
    return [now.month, now.strftime('%Y-%m-%d'), after.month, after.day]
