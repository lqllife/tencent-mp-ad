import datetime
import os
import re
from os import listdir, path
from pathlib import Path
from sys import modules

from playwright.sync_api import Playwright, TimeoutError

from utils.WxError import WxError
from utils.tools import get_new_date, make_rand_arr, make_rand_str, split_list


class Wechat:
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
        
        self.browser = play.chromium.launch(headless=headless, args=args, slow_mo=300, executable_path=self._get_executable_path())
        self.context = self._get_context()
        self.page = self.context.new_page()
        
        self.fastTest = False
        self.materialNo = 0
    
    def _get_context(self):
        """获取浏览器上下文"""
        if self._is_auth():
            return self.browser.new_context(storage_state=self.authPath, no_viewport=self.noViewPort)
        
        return self.browser.new_context(no_viewport=True)
    
    @staticmethod
    def _get_executable_path() -> Path | None:
        """获取playwright执行目录"""
        parent_folder = Path(modules['playwright'].__file__).parent / 'driver' / 'package' / '.local-browsers'
        
        if not path.exists(parent_folder):
            return None
        
        child_folders = [name for name in listdir(parent_folder) if path.isdir(parent_folder / name) and name.strip().lower().startswith('chromium')]
        
        if len(child_folders) != 1:
            return None
        
        chromium_folder = child_folders[0]
        
        return parent_folder / chromium_folder / 'chrome-win' / 'chrome.exe'
    
    @staticmethod
    def _get_age_index(val: int, inc=True):
        """返回年龄的下标"""
        r = range(18, 67)
        idx = r.index(val)
        
        return idx + 1 if inc else idx
    
    def close(self):
        """关闭浏览器"""
        self.context.close()
        self.browser.close()
    
    def close_adq_page(self, with_mp_page=False):
        """关闭公众号页面"""
        if self.adqPage is not None:
            self.adqPage.close()
            self.adqPage = None
        if with_mp_page and self.mpPage is not None:
            self.mpPage.close()
            self.mpPage = None
    
    def reload_pge(self, is_mp=True):
        """刷新mp页面"""
        page = self.mpPage if is_mp else self.adqPage
        page.reload()
        page.wait_for_load_state()
    
    def _is_auth(self) -> bool:
        """认证文件是否存在"""
        return os.path.exists(self.authPath)
    
    def check_login(self) -> bool:
        """检查是否需要登录"""
        self.page.goto('https://e.qq.com/ads/')
        return self._is_dom_exist('link', name='登录')
    
    def login(self, account_id=0):
        """执行登录"""
        if self.fastTest:
            self.page.goto(f'https://ad.qq.com/atlas/{account_id}/ad/create?from=mp')
            self.adqPage = self.page
            return
        
        self.page.goto('https://e.qq.com/ads/')
        if self._is_dom_exist('link', '登录'):
            # 登录过期，删除认证文件
            if self._is_auth():
                os.unlink(self.authPath)
            
            self.page.get_by_role('link', name='登录').click()
            self.page.get_by_role('link', name='微信账号登录').click()
            self.page.wait_for_url(re.compile('home', re.IGNORECASE), timeout=120000)  # 等待120秒
            self.context.storage_state(path=self.authPath)
        else:
            self.page.goto('https://e.qq.com/ams/home')
        
        # 如果登录页面会新开一个页面，则将新开的页面作为 self.page
        
        self.page.goto('https://e.qq.com/ams/agency/advertiser-list/wechat')
    
    def _is_dom_exist(self, role, name='', timeout=None) -> bool:
        """检查dom元素是否存在"""
        try:
            if timeout is None:
                result = self.page.get_by_role(role, name=name).is_visible()
            else:
                result = self.page.wait_for_selector(role, timeout=timeout).is_visible()
            return result
        except TimeoutError:
            return False
    
    def cancle_mobile_alert(self):
        """取消登记手机号的弹窗"""
        if not self._is_dom_exist('button[data-report="phone-not-have-mobile-warn.submit"]', timeout=5000):
            return
        self.page.get_by_role('button', name='去登记手机号').click()
        # try:
        #     self.page.get_by_role('button', name='取消').click(timeout=5000)
        # except TimeoutError:
        #     pass
        # self.page.goto('https://e.qq.com/ams/agency/advertiser-list/wechat')
    
    def chose_account(self, name: str):
        """选择账户"""
        self.page.wait_for_timeout(3000)
        self.page.get_by_placeholder('请输入广告主名称').click()
        self.page.get_by_placeholder('请输入广告主名称').fill(name)
        self.page.locator('i[class="spaui-icon-viewer spaui-icon"]').nth(1).click()
        self.page.wait_for_timeout(3000)
        if not self._is_dom_exist(f'tr:has-text("{name}")', timeout=10000):
            raise WxError(f'未找到公众号[{name}]', 1)
        
        self.materialCount = 0
        dom = self.page.get_by_role('link', name='公众平台投放入口')
        if dom.count() > 1:
            dom = dom.first
        with self.page.expect_popup() as mpPageInfo:
            dom.click()
        self.mpPage = mpPageInfo.value
    
    def _select_material(self, no: int) -> bool:
        """选择素材"""
        try:
            self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('div:nth-child(' + str(no) + ') > .figure-box > .relative > img').click(timeout=5000)
            return True
        except TimeoutError:
            return False
    
    def _get_uploaded_material_num(self):
        """获取已上传的素材数量"""
        btnName = '我的图片' if self._is_image_material() else '我的视频'
        self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_text(f'{btnName}').click()
        try:
            self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('.figure-box').first.wait_for(timeout=20000)
        except TimeoutError:
            pass
        return self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('.figure-box').count()
    
    def _set_material(self):
        self.adqPage.get_by_role('button', name='图片/视频').click()
        # 随机选择图片
        if self.materialCount == 0:
            # 没有素材时，上传素材
            realCount = self._get_uploaded_material_num()
            _, _, lists = self._get_material_list()
            if realCount < len(lists):
                print('需要上传素材', realCount, len(lists), end='')
                self._upload_materials()
        self._chose_material()
    
    def _chose_material(self):
        self.materialCount = self._get_uploaded_material_num()
        # 为了防止随机选择时会出错，随机生成的数组是预选数组的一倍
        if self.materialCount == 0:
            raise WxError('素材上传失败', 1)
        selectCount = int(self.config['material_count'])
        selectedNum = 0
        randArr = make_rand_arr(self.materialCount, selectCount * 2 if self.materialCount >= selectCount * 2 else selectCount, int(self.config['material_start']))
        # print(f'素材总数：{self.materialCount}, 随机：{randArr}', end='')
        for no in randArr:
            if self._select_material(no):
                selectedNum += 1
                if selectedNum >= selectCount:
                    break
        self.adqPage.wait_for_load_state()
        self.adqPage.frame_locator('.spaui-drawer-body > iframe').get_by_role('button', name='确定').click()
    
    def open_plan_page(self, create=True, retry=1):
        """打开新建广告页面"""
        # 重试次数超过三次则不再重试
        if retry > 3:
            raise WxError('公众号详情页面打开失败', 1)
        try:
            self.mpPage.get_by_role('link', name='推广').click()
        except TimeoutError:
            self.reload_pge()
            retry += 1
            return self.open_plan_page(create, retry)
        
        self._close_page_button()
        if create:
            with self.mpPage.expect_popup() as adqPageInfo:
                self.mpPage.get_by_role('button', name='新建广告').click()
            self.adqPage = adqPageInfo.value
    
    def create_plan(self, retry=1):
        """新建推广计划"""
        # 重试次数超过三次则不再重试
        if retry > 3:
            raise WxError('创建计划页面打开失败', 1)
        # 因为网络问题导致页面打开失败
        self._close_page_button(False)
        try:
            self.adqPage.get_by_text('新建推广计划').click()
        except TimeoutError:
            self.reload_pge(False)
            retry += 1
            return self.create_plan(retry)
        self.adqPage.locator('#order_container_campaign').locator('button[data-hottag-content="unfold"]').click()
        self.adqPage.locator('#order_container_campaign').get_by_role('button', name='公众号推广').click()
        self.adqPage.locator('#order_container_campaign').get_by_role('button', name='加速投放').click()
        self.adqPage.locator('#order_container_campaign').get_by_placeholder('请输入推广计划名称').click()
        self.adqPage.locator('#order_container_campaign').get_by_placeholder('请输入推广计划名称').fill('%s-%s-%s' % ('推广计划', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), make_rand_str()))
        self._public_steps()
    
    def copy_plan(self, retry=1):
        """复制现有计划"""
        # 重试次数超过三次则不再重试
        if retry > 3:
            raise WxError('无法复制，公众号没有广告', 1)
        self._close_page_button()
        try:
            if self.mpPage.wait_for_selector(f'tr:has-text("复制")', timeout=20000).is_visible():
                with self.mpPage.expect_popup() as mpPageInfo:
                    self.mpPage.get_by_role('button', name='复制').first.click()
                self.adqPage = mpPageInfo.value
        except TimeoutError:
            self.reload_pge()
            retry += 1
            return self.copy_plan(retry)
        self._close_page_button(False)
        self.adqPage.wait_for_load_state()
        try:
            # 因为网络问题导致页面打开失败
            self.adqPage.get_by_placeholder('广告名称仅用于管理广告，不会对外展示').click()
        except TimeoutError:
            self.reload_pge(False)
            retry += 1
            return self.copy_plan(retry)
        self.adqPage.get_by_placeholder('广告名称仅用于管理广告，不会对外展示').fill('%s-%s-%s' % ('微信公众号与小程序', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), make_rand_str()))
        self.adqPage.get_by_role("button", name='清空').click()
        self.adqPage.get_by_role("button", name='确定').click()
        self._set_material()
        self.adqPage.get_by_role('button', name='原生推广页').click()
        self.adqPage.get_by_role('button', name='微信公众号详情').click()
        self.adqPage.wait_for_timeout(2000)
        self._submit()
    
    def _close_page_button(self, is_mp=True):
        """关闭 我知道了 按钮"""
        try:
            page = self.mpPage if is_mp else self.adqPage
            page.get_by_role('dialog').get_by_role('button', name='我知道了').click(timeout=6000)
        except TimeoutError:
            pass
    
    def _is_image_material(self) -> bool:
        """是不是上传图片素材"""
        return self.config['material_type'] == '1'
    
    def _public_steps(self):
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
        idx = self._get_age_index(int(self.config['age'][0]))
        self.adqPage.locator('.selection-info').nth(idx).click()
        # 年龄 - 右侧
        self.adqPage.locator('.selection-single').nth(1).click()
        idx = self._get_age_index(int(self.config['age'][1]), False)
        self.adqPage.locator('.selection-info').nth(idx).click()
        self.adqPage.get_by_role('button', name='男').click()
        # 选择投放日期
        [monthNow, now, monthAfter, dayAfter] = get_new_date()
        self.adqPage.get_by_text(f'开始日期{now}').click()
        if monthNow != monthAfter:
            self.adqPage.locator(".roll > svg").click()
        dayDom = self.adqPage.locator("#order_container_adgroup").get_by_text(str(dayAfter), exact=True)
        if dayDom.count() == 0:
            dayDom.click()
        else:
            dayDom.nth(0 if dayAfter < 20 else 1).click()
        # 出价方式
        if self._is_image_material():
            self.adqPage.get_by_role('button', name='oCPC').click()
        self.adqPage.locator('.selection-single').nth(2).click()
        self.adqPage.locator('.selection-info').nth(0).click()
        self.adqPage.get_by_role('button', name='优先拿量').click()
        inputNo = 1
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo).click()
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo).fill(str(self.config['price']))
        # 一键起量
        if int(self.config['budget']) > 0:
            self.adqPage.locator('[data-hottag="Click.Function.Phoenix.CostGroup.AutoAcquisition.SwitchBtn"]').click()
            self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo + 1).click()
            self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo + 1).fill(str(self.config['budget']))
        self.adqPage.get_by_placeholder('广告名称仅用于管理广告，不会对外展示').click()
        self.adqPage.get_by_placeholder('广告名称仅用于管理广告，不会对外展示').fill('%s-%s-%s' % ('微信公众号与小程序', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), make_rand_str()))
        self.adqPage.get_by_role('button', name='下一步').click()
        self.adqPage.wait_for_load_state()
        if self.adqPage.get_by_role('switch', name='自动衍生更多素材').locator('span').first.is_checked():
            self.adqPage.get_by_role('switch', name='自动衍生更多素材').locator('span').first.click()
        if self.adqPage.get_by_role('switch', name='自动衍生更多文案').locator('span').first.is_checked():
            self.adqPage.get_by_role('switch', name='自动衍生更多文案').locator('span').first.click()
        self._set_material()
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo + 3).click()
        self.adqPage.locator('.meta-input.spaui-input.has-normal').nth(inputNo + 3).fill(self.config['title'])
        self.adqPage.get_by_role('button', name='微信公众号详情').click()
        self._submit()
    
    def _upload_materials(self):
        """上传素材"""
        # 点击本地上传
        self.adqPage.frame_locator('.spaui-drawer-body > iframe').locator('a[data-hottag="MaterialLibrary.DynamicCreativeMaterialDialog.Click.MaterialTabClick.PageTab1"]').click()
        MaterialPath, fileNames, files = self._get_material_list()
        for file in files:
            fileNames.append(os.path.join(MaterialPath, file))
        fileChunk = split_list(fileNames, 10)
        for filesArr in fileChunk:
            with self.adqPage.expect_file_chooser() as fc_info:
                self.adqPage.frame_locator(".spaui-drawer-body > iframe").get_by_text('点击或拖拽上传').click()
            file_chooser = fc_info.value
            file_chooser.set_files(filesArr)
            timeout = (2000 if len(filesArr) < 10 else 20000) + 1500 * len(filesArr) * (1 if self._is_image_material() else 5)
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
    
    def _get_material_list(self):
        """获取素材文件的数组"""
        MaterialPath = 'images' if self._is_image_material() else 'videos'
        MaterialPath = f'conf/{MaterialPath}'
        fileNames = []
        files = os.listdir(MaterialPath)
        return MaterialPath, fileNames, files
    
    def _submit(self, retry=1):
        """提交计划"""
        # 重试次数达到8次则放弃提交
        if retry > 8:
            raise WxError('素材不合规')
        self.adqPage.get_by_role('button', name='提交').click()
        # 素材不合规
        try:
            if self.adqPage.locator('div:has-text("提交数据不符合审核规范，请进行检查"), div:has-text("素材数据异常")').count() != 0:
                if retry == 1:
                    print(f'素材不合规,重选x{retry} ', end='')
                else:
                    print(f'x{retry} ', end='')
                self.adqPage.wait_for_timeout(1000)
                self.adqPage.get_by_role('button', name='清空').click()
                self.adqPage.get_by_role('button', name='确定').click()
                self.adqPage.wait_for_timeout(1500)
                self._set_material()
                retry += 1
                self.adqPage.wait_for_timeout(800 * retry)
                return self._submit(retry)
        except TimeoutError:
            pass
        self.adqPage.wait_for_timeout(1500)
        self.adqPage.get_by_role('button', name='提交广告').click()
        try:
            self.adqPage.get_by_role('button', name='关闭').wait_for(timeout=8000)
            self.adqPage.close()
        except TimeoutError:
            pass
