import os.path
import time

from playwright.sync_api import sync_playwright, TimeoutError, Error

from utils.WxError import WxError
from utils.config import Conf
from utils.tools import get_log_file_path, log_error
from wechat import Wechat


class Main:
    # 处理失败的公众号数量
    failNum = 0
    play = None
    time = time.time()
    
    def __init__(self):
        logPath = get_log_file_path()
        self.log = log_error(logPath, '检查')
        self._print_and_log('------------------------------------------------------------')
        print('程序启动，检查配置中...')
        confs = Conf('conf/config.ini')
        self.config = confs.get_configs()
        print('配置项无误')
        self.officials = self.config['officials']
    
    def check_login(self):
        """是否需要登录"""
        self._print_and_log('检查是否需要登录...')
        if not os.path.exists('auth/auth.json'):
            print('请扫码登录')
            p = Wechat(playwright, {}, True)
            p.login()
            p.close()
            print('登录成功，开始处理...')
        else:
            p = Wechat(playwright, {}, True)
            if p.check_login():
                print('请扫码登录')
                p.login()
            else:
                print('无需登录，开始处理...')
            p.close()
    
    def start_plan(self):
        """执行计划"""
        self._check_fail_official()
        if self.failNum == 0:
            return
        
        officialIndex = 1
        for name in self.officials:
            count = self.officials[name]['count']
            if count == 0:
                continue
            self.time = time.time()
            try:
                print()
                print(f'公众号[{name}][{officialIndex}/{self.failNum}]，需要创建{count}个计划')
                self.play.chose_account(name)
                i = 0
                for i in range(count):
                    print(f'{time.strftime("%H:%M:%S")} 第{i + 1}个计划 ', end='')
                    try:
                        if i == 0:
                            self.play.open_plan_page()
                            self.play.create_plan()
                            self.play.close_adq_page()
                            self.play.reload_pge()
                        else:
                            self.play.copy_plan()
                        print(f'[成功] 耗时: {self._get_time_diff()}s')
                        self.officials[name]['count'] -= 1
                        time.sleep(2)
                    except (WxError, TimeoutError, Error) as err:
                        print(f'[错误，将在稍后重试] 耗时: {self._get_time_diff()}s')
                        self.log.error(f'公众号[{name}]第[{i + 1}/{count}]个计划发生错误：{err}，耗时: {self._get_time_diff()}s')
                        self.play.close_adq_page()
                        if i == 0:
                            self.play.open_plan_page()
                        if isinstance(err, WxError) and err.errorcode == 1:
                            break
                        else:
                            continue
                self.play.close_adq_page(True)
                left = self.officials[name]["count"]
                txt = '' if left == 0 else f'，剩下的{left}个计划将于稍后重试'
                self._print_and_log(f'公众号[{name}]的{count - left}个计划创建成功' + txt)
                officialIndex += 1
            except (TimeoutError, Error) as err:
                officialIndex += 1
                print('出现错误，将在稍后重试')
                self.log.error(f'公众号[{name}]发生错误：{err}')
                self.play.close_adq_page(True)
                continue
            except WxError as err:
                officialIndex += 1
                print('出现错误，将在稍后重试')
                self.log.error(f'公众号[{name}]出现错误：{err}')
                if err.errorcode == 1:
                    self.officials[name]['count'] = 0
                continue
        self._check_fail_official()
    
    def _get_time_diff(self):
        """获取时间差并更新时间"""
        diff = time.time() - self.time
        self.time = time.time()
        return round(diff, 2)
    
    def _check_fail_official(self):
        """检查处理失败的公众号数量"""
        self.failNum = 0
        for name in self.officials:
            if self.officials[name]['count'] != 0:
                self.failNum += 1
    
    def run(self):
        officialStr = ''
        for nameStr in self.officials:
            officialStr += nameStr + ','
        self._print_and_log(f'本次需要处理{len(self.officials)}个公众号：{officialStr.rstrip(",")}，每个公众号创建{self.config["count"]}个计划')
        self.play = Wechat(playwright, self.config, bool(int(self.config['headless'])))
        self.play.login()
        self.play.cancle_mobile_alert()
        self.start_plan()
        while self.failNum != 0:
            self._print_and_log(f'~~~~~~~~~~~~~~~~ 正在重试失败的{self.failNum}个公众号 ~~~~~~~~~~~~~~~~')
            self.start_plan()
        self.play.close()
        self._print_and_log('所有公众号已处理完成，程序退出')
        self._print_and_log('============================================================\n')
    
    def _print_and_log(self, logStr):
        """打印并存储日志"""
        print(logStr)
        self.log.info(logStr)


with sync_playwright() as playwright:
    main = Main()
    main.check_login()
    main.run()
