import time

from playwright.sync_api import sync_playwright, TimeoutError

from utils.WxError import WxError
from utils.config import Conf
from utils.tools import getLogFilePath, logError
from wechat import Play

logPath = getLogFilePath()
log = logError(logPath, '检查')

try:
    confs = Conf('conf/config.ini')
    config = confs.getConfigs()
    log.info('配置项无误')
except WxError as error:
    log.error(error)
    exit(1)

with sync_playwright() as playwright:
    play = Play(playwright, config, True)
    play.fastTest = True
    play.login()
    play.cancleMobileAlert()
    play.choseAccount('捗读')
    # play.openPlanPage(False)
    play.openPlanPage()
    # play.adqPage = play.page
    play.createPlanByNew()
    # play.createPlanByCurrent(play.page)
    # play.createPlanByCopy()
    # play.closeAdqPage()
    # play.close()
    time.sleep(10000)
    log.info('程序退出\n')
