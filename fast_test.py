import time

from playwright.sync_api import sync_playwright

from utils.WxError import WxError
from utils.config import Conf
from utils.tools import get_log_file_path, log_error
from wechat import Wechat

logPath = get_log_file_path()
log = log_error(logPath, '检查')

try:
    confs = Conf('conf/config.ini')
    config = confs.get_configs()
    log.info('配置项无误')
except WxError as error:
    log.error(error)
    exit(1)

with sync_playwright() as playwright:
    play = Wechat(playwright, config, True)
    play.fastTest = True
    play.login(30976118)
    play.create_plan()
    time.sleep(10000)
    log.info('程序退出\n')
