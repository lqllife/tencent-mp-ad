from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth/auth.json")
    page = context.new_page()
    page.goto("https://e.qq.com/ads/")
    page.goto("https://e.qq.com/ams/agency/advertiser-list/wechat")
    page.get_by_role("button", name="去登记手机号").click()
    page.get_by_role("button", name="取消").click()
    with page.expect_popup() as page1_info:
        page.get_by_role("row", name="蚌闻 30184059 wx48dbd9a237827f11 - 已授权 公众号 0.10 - - - 长沙浪哥-Qishiqi,长沙浪哥- fuyu_6,长沙浪哥-cwh1999,长沙浪哥-md01062 编辑 公众平台投放入口ADQ投放入口收藏账户帐号档案任务指南").get_by_role("link", name="公众平台投放入口").click()
    page1 = page1_info.value
    page1.get_by_role("link", name="资产").click()
    page1.frame_locator("iframe[title=\"腾讯广告 - 资产\"]").get_by_role("button", name="我知道了").click()
    with page1.expect_popup() as page2_info:
        page1.frame_locator("iframe[title=\"腾讯广告 - 资产\"]").get_by_role("link", name="我的素材 整合广告投放使用的创意素材，进行素材的集中管理和维护").click()
    page2 = page2_info.value
    page2.frame_locator("iframe[title=\"myMaterialIframe\"]").locator("a").filter(has_text="图片").click()
    page2.frame_locator("iframe[title=\"myMaterialIframe\"]").get_by_role("button", name="上传素材").click()
    page2.frame_locator("iframe[title=\"myMaterialIframe\"]").get_by_text("点击上传").click()
    page2.frame_locator("iframe[title=\"myMaterialIframe\"]").get_by_role("dialog").set_input_files(["1.1.jpg", "1.2.jpg", "1.3.jpg", "1.4.jpg", "1.5.jpg", "1.6.jpg", "1.7.jpg", "1.8.jpg", "1.9.jpg", "1.10.jpg", "1.11.jpg", "1.12.jpg"])
    page2.frame_locator("iframe[title=\"myMaterialIframe\"]").locator("#spaui-uploader_2-empty div").click()
    page2.frame_locator("iframe[title=\"myMaterialIframe\"]").get_by_role("dialog").set_input_files(["1.1.jpg", "1.2.jpg", "1.3.jpg", "1.4.jpg", "1.5.jpg", "1.6.jpg", "1.7.jpg", "1.8.jpg", "1.9.jpg", "1.10.jpg"])
    page2.frame_locator("iframe[title=\"myMaterialIframe\"]").get_by_role("button", name="确定").click()
    page2.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
