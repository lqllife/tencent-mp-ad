import datetime
import random
import logging


def makeRandArr(length, count, start=0):
    """生成随机字符串数组"""
    arr = list()
    while len(arr) != count:
        rand = random.randint(1, length - start)
        if arr.count(rand) == 0:
            arr.append(rand)
    
    # arr.sort()
    return arr


def makeRandStr(length=6):
    """生成随机字符串"""
    randList = random.sample('zyxwvutsrqponmlkjihgfedcba', length)
    return ''.join(randList)


def splitList(arr: list, n: int):
    """数组分片"""
    return [arr[i:i + n] for i in range(0, len(arr), n)]


def getTime():
    """获取日志"""
    return datetime.datetime.now().strftime('%Y-%m-%d')


def getLogFilePath():
    """返回日志文件目录"""
    return 'logs/' + getTime() + '.txt'


def logError(log_path, logging_name='', console=False):
    """
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :param console: 是否在console中输出
    :return:
    """
    '''
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
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


def getNewDate():
    """获取15天后的日期"""
    now = datetime.datetime.now()
    after = now + datetime.timedelta(days=15)
    return [now.month, now.strftime('%Y-%m-%d'), after.month, after.day]
