import os.path
import re
import datetime
from sys import modules
from os import listdir, path
from pathlib import Path
from typing import Union

from playwright.sync_api import Playwright, TimeoutError

from utils.WxError import WxError
from utils.tools import getNewDate, makeRandArr, makeRandStr, splitList


def get_executable_path() -> Union[str, None]:
    """获取playwright执行目录"""
    parent_folder = Path(modules['playwright'].__file__).parent / 'driver' / 'package' / '.local-browsers'
    
    if not path.exists(parent_folder):
        return None
    
    child_folders = [name for name in listdir(parent_folder) if path.isdir(parent_folder / name) and name.strip().lower().startswith('chromium')]
    
    if len(child_folders) != 1:
        return None
    
    chromium_folder = child_folders[0]
    
    return parent_folder / chromium_folder / 'chrome-win' / 'chrome.exe'


class Play:
    authPath = 'auth/auth.json'
    page = None
    mpPage = None
    adqPage = None
    
    def __init__(self, play: Playwright, config: dict, show_headless=False):
        """初始化"""
        self.config = config
        self.materialCount = 0
        # 判断是否是无头模式
        if show_headless:
            headless = False
            self.noViewPort = True
            args = ['--start-maximized']
        else:
            headless = True
            self.noViewPort = False
            args = None
        
        self.browser = play.chromium.launch(headless=headless, args=args, slow_mo=300, executable_path=get_executable_path())
        self.context = self.getContext()
        self.page = self.context.new_page()
        
        self.fastTest = False
        self.materialNo = 0
    
    def close(self):
        """关闭浏览器"""
        self.context.close()
        self.browser.close()
    
    def closeAdqPage(self, withMpPage=False):
        """关闭公众号页面"""
        if self.adqPage is not None:
            self.adqPage.close()
            self.adqPage = None
        if withMpPage and self.mpPage is not None:
            self.mpPage.close()
            self.mpPage = None
    
    def reloadMpPge(self):
        """刷新mp页面"""
        self.mpPage.reload()
        self.mpPage.wait_for_load_state()
    
    def getContext(self):
        """获取浏览器上下文"""
        if self.isAuth():
            return self.browser.new_context(storage_state=self.authPath, no_viewport=self.noViewPort)
        
        return self.browser.new_context(no_viewport=True)
    
    def isAuth(self) -> bool:
        """认证文件是否存在"""
        return os.path.exists(self.authPath)
    
    def checkLogin(self) -> bool:
        """检查是否需要登录"""
        self.page.goto('https://e.qq.com/ads/')
        return self.isDomExist('link', name='登录')
    
    def login(self, accountId=0):
        """执行登录"""
        if self.fastTest:
            self.page.goto(f'https://ad.qq.com/atlas/{accountId}/ad/create?from=mp')
            self.adqPage = self.page
            return
        
        self.page.goto('https://e.qq.com/ads/')
        if self.isDomExist('link', '登录'):
            # 登录过期，删除认证文件
            if self.isAuth():
                os.unlink(self.authPath)
            
            self.page.get_by_role('link', name='登录').click()
            self.page.get_by_role('link', name='微信账号登录').click()
            self.page.wait_for_url(re.compile('home', re.IGNORECASE), timeout=120000)  # 等待120秒
            self.context.storage_state(path=self.authPath)
        else:
            self.page.goto('https://e.qq.com/ams/home')
        
        # 如果登录页面会新开一个页面，则将新开的页面作为 self.page
        
        self.page.goto('https://e.qq.com/ams/agency/advertiser-list/wechat')
    
    def isDomExist(self, role, name='', timeout=None):
        """检查dom元素是否存在"""
        try:
            if timeout is None:
                result = self.page.get_by_role(role, name=name).is_visible()
            else:
                result = self.page.wait_for_selector(role, timeout=timeout).is_visible()
            return result
        except TimeoutError:
            return False
    
    def cancleMobileAlert(self):
        """取消登记手机号的弹窗"""
        if not self.isDomExist('button[data-report="phone-not-have-mobile-warn.submit"]', timeout=5000):
            return
        self.page.get_by_role('button', name='去登记手机号').click()
        # try:
        #     self.page.get_by_role('button', name='取消').click(timeout=5000)
        # except TimeoutError:
        #     pass
        # self.page.goto('https://e.qq.com/ams/agency/advertiser-list/wechat')
    
    def choseAccount(self, name: str):
        """选择账户"""
        self.page.wait_for_timeout(3000)
        self.page.get_by_placeholder('请输入广告主名称').click()
        self.page.get_by_placeholder('请输入广告主名称').fill(name)
        self.page.locator('i[class="spaui-icon-viewer spaui-icon"]').nth(1).click()
        self.page.wait_for_timeout(3000)
        if not self.isDomExist(f'tr:has-text("{name}")', timeout=10000):
            raise WxError(f'未找到公众号[{name}]', 1)
        
        self.materialCount = 0
        with self.page.expect_popup() as mpPageInfo:
            self.page.get_by_role('link', name='公众平台投放入口').click()
        self.mpPage = mpPageInfo.value
    
    def selectMaterila(self, no: int) -> bool:
        """选择素材"""
        try:
            self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('div:nth-child(' + str(no) + ') > .figure-box > .relative > img').click(timeout=5000)
            return True
        except TimeoutError:
            return False
    
    def setMaterial(self):
        if self.adqPage.get_by_role('switch', name='自动衍生更多素材').locator('span').first.is_checked():
            self.adqPage.get_by_role('switch', name='自动衍生更多素材').locator('span').first.click()
        if self.adqPage.get_by_role('switch', name='自动衍生更多文案').locator('span').first.is_checked():
            self.adqPage.get_by_role('switch', name='自动衍生更多文案').locator('span').first.click()
        self.adqPage.get_by_role('button', name='图片/视频').click()
        # 随机选择图片
        btnName = '我的图片' if self.isImageMaterial() else '我的视频'
        self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_text(f'{btnName}').click()
        try:
            self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('.figure-box').first.wait_for(timeout=20000)
        except TimeoutError:
            pass
        if self.materialCount == 0:
            # 没有素材时，上传素材
            realCount = self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('.figure-box').count()
            _, _, lists = self.getMaterialList()
            if realCount < len(lists):
                print('需要上传素材', realCount, len(lists))
                self.uploadMaterials()
            self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_text(f'{btnName}').click()
            self.materialCount = self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('.figure-box').count()
        # 为了防止随机选择时会出错，随机生成的数组是预选数组的一倍
        if self.materialCount == 0:
            raise WxError('素材上传失败', 1)
        selectCount = int(self.config['material_count'])
        selectedNum = 0
        randArr = makeRandArr(self.materialCount, selectCount * 2 if self.materialCount >= selectCount * 2 else selectCount, int(self.config['material_start']))
        print(f'素材总数：{self.materialCount}, 随机：{randArr}')
        for no in randArr:
            if self.selectMaterila(no):
                selectedNum += 1
                if selectedNum >= selectCount:
                    break
        self.adqPage.wait_for_load_state()
        self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_role('button', name='确定').click()
    
    def openPlanPage(self, create=True):
        """打开新建广告页面"""
        self.mpPage.get_by_role('link', name='推广').click()
        self.closePageButton()
        if create:
            with self.mpPage.expect_popup() as adqPageInfo:
                self.mpPage.get_by_role('button', name='新建广告').click()
            self.adqPage = adqPageInfo.value
    
    def createPlan(self):
        """新建推广计划"""
        self.closePageButton(False)
        self.adqPage.get_by_text('新建推广计划').click()
        self.adqPage.locator('#order_container_campaign').locator('button[data-hottag-content="unfold"]').click()
        self.adqPage.locator('#order_container_campaign').get_by_role('button', name='公众号推广').click()
        self.adqPage.locator('#order_container_campaign').get_by_role('button', name='加速投放').click()
        self.adqPage.locator('#order_container_campaign').get_by_placeholder('请输入推广计划名称').click()
        self.adqPage.locator('#order_container_campaign').get_by_placeholder('请输入推广计划名称').fill('%s-%s-%s' % ('推广计划', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), makeRandStr()))
        self.publicSteps()
    
    def copyPlan(self):
        """复制现有计划"""
        self.closePageButton()
        try:
            if self.mpPage.wait_for_selector(f'tr:has-text("复制")', timeout=20000).is_visible():
                with self.mpPage.expect_popup() as mpPageInfo:
                    self.mpPage.get_by_role('button', name='复制').first.click()
                self.adqPage = mpPageInfo.value
        except TimeoutError:
            raise WxError('无法复制，公众号没有广告', 1)
        self.closePageButton(False)
        self.adqPage.wait_for_load_state()
        self.adqPage.get_by_placeholder('广告名称仅用于管理广告，不会对外展示').click()
        self.adqPage.get_by_placeholder('广告名称仅用于管理广告，不会对外展示').fill('%s-%s-%s' % ('微信公众号与小程序', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), makeRandStr()))
        self.adqPage.get_by_role("button", name='清空').click()
        self.adqPage.get_by_role("button", name='确定').click()
        self.setMaterial()
        self.adqPage.get_by_role('button', name='原生推广页').click()
        self.adqPage.get_by_role('button', name='微信公众号详情').click()
        self.adqPage.wait_for_timeout(2000)
        self.submit(False)
        self.adqPage.close()
    
    def closePageButton(self, isMp=True):
        """关闭 我知道了 按钮"""
        try:
            page = self.mpPage if isMp else self.adqPage
            page.get_by_role('dialog').get_by_role('button', name='我知道了').click(timeout=6000)
        except TimeoutError:
            pass
    
    def isImageMaterial(self) -> bool:
        """是不是上传图片素材"""
        return self.config['material_type'] == '1'
    
    @staticmethod
    def getAgeIndex(val: int, inc=True):
        """返回年龄的下标"""
        r = range(18, 67)
        idx = r.index(val)
        
        return idx + 1 if inc else idx
    
    def publicSteps(self):
        """公共提交步骤"""
        self.adqPage.get_by_role('button', name='下一步').click()
        self.adqPage.wait_for_load_state()
        self.adqPage.wait_for_timeout(6000)
        self.adqPage.get_by_role('button', name='不使用').click()
        # 从已有推广计划创建时不需要点此
        self.adqPage.get_by_role('button', name=re.compile('微信公众号与小程序')).click()
        # 更多选项
        if self.config['position'] != '不限':
            try:
                self.adqPage.get_by_role('button', name='更多选项').click(timeout=1500)
            except TimeoutError:
                pass
            self.adqPage.locator('#target_item_wechat_position').get_by_role('button', name='自定义').click()
            for p in self.config['position']:
                self.adqPage.get_by_text(f'{p}').click()
        self.adqPage.get_by_role('button', name='按区域').click()
        self.adqPage.get_by_text('近期到访').click()
        self.adqPage.get_by_text('常住地', exact=True).click()
        self.adqPage.get_by_role('button', name='批量导入区域').click()
        # 文件上传
        with self.adqPage.expect_file_chooser() as fc_info:
            self.adqPage.get_by_role('button', name='上传文件').click()
        file_chooser = fc_info.value
        file_chooser.set_files('conf/腾讯广告已选择地域定向导出信息.txt')
        # 这里改成正则匹配
        self.adqPage.get_by_role('button', name=re.compile(r'导入\s\d+\s个区域')).click()
        # 年龄
        self.adqPage.locator('[data-hottag="Click.Function.Phoenix.TargetItem.age.customize"]').click()
        # 年龄 - 左侧
        self.adqPage.locator('.selection-single').nth(0).click()
        idx = self.getAgeIndex(int(self.config['age'][0]))
        self.adqPage.locator('.selection-info').nth(idx).click()
        # 年龄 - 右侧
        self.adqPage.locator('.selection-single').nth(1).click()
        idx = self.getAgeIndex(int(self.config['age'][1]), False)
        self.adqPage.locator('.selection-info').nth(idx).click()
        self.adqPage.get_by_role('button', name='男').click()
        # 选择投放日期
        [monthNow, now, monthAfter, dayAfter] = getNewDate()
        self.adqPage.get_by_text(f'开始日期{now}').click()
        if monthNow != monthAfter:
            self.adqPage.locator(".roll > svg").click()
        dayDom = self.adqPage.locator("#order_container_adgroup").get_by_text(str(dayAfter), exact=True)
        if dayDom.count() == 0:
            dayDom.click()
        else:
            dayDom.nth(0).click()
        # 出价方式
        if self.isImageMaterial():
            self.adqPage.get_by_role('button', name='oCPC').click()
        self.adqPage.locator('.selection-single').nth(2).click()
        self.adqPage.locator('.selection-info').nth(0).click()
        self.adqPage.get_by_role('button', name='优先拿量').click()
        inputNo = 1
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo).click()
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo).fill(str(self.config['price']))
        self.adqPage.locator('[data-hottag="Click.Function.Phoenix.CostGroup.AutoAcquisition.SwitchBtn"]').click()
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo + 1).click()
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo + 1).fill(str(self.config['budget']))
        self.adqPage.get_by_placeholder('广告名称仅用于管理广告，不会对外展示').click()
        self.adqPage.get_by_placeholder('广告名称仅用于管理广告，不会对外展示').fill('%s-%s-%s' % ('微信公众号与小程序', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), makeRandStr()))
        self.adqPage.get_by_role('button', name='下一步').click()
        self.adqPage.wait_for_load_state()
        self.setMaterial()
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo + 3).click()
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo + 3).fill(self.config['title'])
        self.adqPage.get_by_role('button', name='微信公众号详情').click()
        self.submit()
    
    def uploadMaterials(self):
        """上传素材"""
        # 点击本地上传
        self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('a[data-hottag="MaterialLibrary.DynamicCreativeMaterialDialog.Click.MaterialTabClick.PageTab1"]').click()
        MaterialPath, fileNames, files = self.getMaterialList()
        for file in files:
            fileNames.append(os.path.join(MaterialPath, file))
        fileChunk = splitList(fileNames, 10)
        for filesArr in fileChunk:
            with self.adqPage.expect_file_chooser() as fc_info:
                self.adqPage.frame_locator(".spaui-drawer-body > iframe").get_by_text('点击或拖拽上传').click()
            file_chooser = fc_info.value
            file_chooser.set_files(filesArr)
            timeout = (2000 if len(filesArr) < 10 else 20000) + 1500 * len(filesArr) * (1 if self.isImageMaterial() else 5)
            self.adqPage.wait_for_timeout(timeout)
            # 有需要重试的素材直接跳过，测试发现无论重试多少次，都是不会成功
            if self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_text('重试').count() != 0:
                self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_role('button', name='取消', exact=True).click()
                break
            # 重试
            # while self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_text('重试').count() != 0:
            #     retryCount = self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_text('重试').count()
            #     print('重试', retryCount)
            #     for i in range(retryCount):
            #         self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_text('重试').nth(i).click()
            #     self.adqPage.wait_for_timeout(3000)
            self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_role('button', name='确定').click(timeout=timeout)
            self.adqPage.wait_for_timeout(1500)
            self.adqPage.get_by_role('button', name='清空').click()
            self.adqPage.get_by_role('button', name='确定').click()
            self.adqPage.wait_for_timeout(4000)
            self.adqPage.get_by_role('button', name='图片/视频').click()
        self.adqPage.wait_for_timeout(3000)
    
    def getMaterialList(self):
        """获取素材文件的数组"""
        MaterialPath = 'images' if self.isImageMaterial() else 'videos'
        MaterialPath = f'conf/{MaterialPath}'
        fileNames = []
        files = os.listdir(MaterialPath)
        return MaterialPath, fileNames, files
    
    def submit(self, close=True):
        """提交计划"""
        self.adqPage.get_by_role('button', name='提交').click()
        self.adqPage.wait_for_timeout(2000)
        self.adqPage.get_by_role('button', name='提交广告').click()
        if close:
            self.adqPage.get_by_role('button', name='关闭').click()
        else:
            try:
                self.adqPage.get_by_role('button', name='关闭').wait_for(timeout=8000)
            except TimeoutError:
                pass
