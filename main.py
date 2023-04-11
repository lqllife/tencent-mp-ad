import os.path
import time

from playwright.sync_api import sync_playwright, TimeoutError, Error

from utils.WxError import WxError
from utils.config import Conf
from utils.tools import getLogFilePath, logError
from wechat import Play


class Main:
    # 处理失败的公众号数量
    failNum = 0
    play = None
    
    def __init__(self):
        logPath = getLogFilePath()
        self.log = logError(logPath, '检查')
        self.log.info('------------------------------------------------------------')
        self.log.info('程序启动，检查配置中...')
        confs = Conf('conf/config.ini')
        self.config = confs.getConfigs()
        self.log.info('配置项无误')
        self.officials = self.config['officials']
    
    def checkLogin(self):
        """是否需要登录"""
        self.log.info('检查是否需要登录...')
        if not os.path.exists('auth/auth.json'):
            self.log.info('请扫码登录')
            p = Play(playwright, {}, True)
            p.login()
            p.close()
            self.log.info('登录成功，开始处理...')
        else:
            p = Play(playwright, {}, True)
            if p.checkLogin():
                self.log.info('请扫码登录')
                p.login()
            else:
                self.log.info('无需登录，开始处理...')
            p.close()
    
    def startPlan(self):
        """执行计划"""
        self.checkFailOfficial()
        if self.failNum == 0:
            return
        
        officialIndex = 1
        for name in self.officials:
            count = self.officials[name]['count']
            if count == 0:
                continue
            try:
                self.log.info(f'公众号[{name}][{officialIndex}/{self.failNum}]，需要创建{count}个计划，开始查找账户')
                self.play.choseAccount(name)
                self.log.info(f'公众号[{name}]账户查找成功，开始创建计划...')
                for i in range(count):
                    try:
                        self.log.info(f'公众号[{name}]第[{i + 1}/{count}]个计划创建中...')
                        if i == 0:
                            self.play.openPlanPage()
                            self.play.createPlan()
                            self.play.closeAdqPage()
                            self.play.reloadMpPge()
                        else:
                            self.play.copyPlan()
                        self.log.info(f'公众号[{name}]第[{i + 1}/{count}]个计划创建成功')
                        self.officials[name]['count'] -= 1
                        time.sleep(2)
                    except (WxError, TimeoutError, Error) as err:
                        self.log.error(f'公众号[{name}]第[{i + 1}/{count}]个计划发生错误：{err}')
                        self.play.closeAdqPage()
                        if i == 0:
                            self.play.openPlanPage()
                        if isinstance(err, WxError) and err.errorcode == 1:
                            break
                        else:
                            continue
                self.play.closeAdqPage(True)
                self.log.info(f'公众号[{name}]的{count}个计划创建成功')
                officialIndex += 1
            except (TimeoutError, Error) as err:
                officialIndex += 1
                self.log.error(f'公众号[{name}]发生错误：{err}')
                self.play.closeAdqPage(True)
                continue
            except WxError as err:
                officialIndex += 1
                self.log.error(f'公众号[{name}]出现错误：{err}')
                if err.errorcode == 1:
                    self.officials[name]['count'] = 0
                continue
        self.checkFailOfficial()
    
    def checkFailOfficial(self):
        """检查处理失败的公众号数量"""
        self.failNum = 0
        for name in self.officials:
            if self.officials[name]['count'] != 0:
                self.failNum += 1
    
    def run(self):
        officialStr = ''
        for nameStr in self.officials:
            officialStr += nameStr + ','
        self.log.info(f'本次需要处理{len(self.officials)}个公众号：{officialStr.rstrip(",")}，每个公众号创建{self.config["count"]}个计划')
        self.play = Play(playwright, self.config, bool(int(self.config['headless'])))
        self.play.login()
        self.play.cancleMobileAlert()
        self.startPlan()
        while self.failNum != 0:
            self.log.info(f'~~~~~~~~~~~~~~~~ 正在重试失败的{self.failNum}个公众号 ~~~~~~~~~~~~~~~~')
            self.startPlan()
        self.play.close()
        self.log.info('所有公众号已处理完成，程序退出')
        self.log.info('============================================================\n')


with sync_playwright() as playwright:
    main = Main()
    main.checkLogin()
    main.run()
