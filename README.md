项目是基于`playwright`开发，用于自动提交腾讯mp广告，非adq广告。

项目为公司自用且自身技术能力有限，虽基本流程是能走通，但仍有很多不规范、妥协和逻辑不完整的地方。

此项目公司已停用，所以我基本上将不再维护，您可以根据自己的需求二次开发。

## 目录结构
```
├── auth # 存放登录的文件
│   └── auth.json # 登录后，文件会自动生成，删除后需要重新登录
├── conf # 配置项
│   ├── images # 存放图片的素材文件夹，文件名不要包含中文
│   ├── videos # 存放视频的素材文件夹，文件名不要包含中文
│   ├── config.ini # 程序的配置文件，需要先修改配置文件才能运行主程序
│   └── 腾讯广告已选择地域定向导出信息.txt # 导出的地域定向文件
├── env # pycharm创建的VirtualEnv，打包时依赖此文件夹
├── cmd # powershell脚本
│   ├── clean.ps1 # 清理打包后生成的缓存和文件
│   ├── deply.ps1 # 复制文件脚本，在实际应用中，我们会复制多份，此脚本为了方便每次更新代码后能一键替换新程序
│   └── pack.ps1 # 用于打包生成文件并复制一些初始化文件
├── logs # 日志，程序每次运行时日志都会记录在此文件夹，日志文件按天创建
│   ├── 2023-02-20.txt
│   └── ······.txt
├── pack # 打包后相关的文件夹
│   ├── build # pyinstaller打包时生成的文件
│   ├── dist # 打包后的完整文件包含一些配置项，详情查看docs.md
│   └── wechat.ico # 主程序的logo
├── utils # 一些工具类
│   ├── config.py # 配置类
│   ├── tools.py # 一些自定义方法
│   └── WxError.py # 异常类
├── docs.md # 
├── fast_test.py # 用于快速测试，直接跳转到创建广告页面
├── main.py # 程序主入口
└── wechat.py # playwright具体业务
```

## 存在的问题
1. 扫码授权登录时，扫码的微信号只能绑定一个服务商，未适配多个服务商的情况。多个服务商时，可将第一个tab页的地址手动替换成点击某个服务商跳转后页面的地址
2. 项目中存在大量使用[wait_for_timeout](https://playwright.dev/python/docs/api/class-page#page-wait-for-timeout)等待元素出现或等待素材上传完成， 但playwright官方不建议使用
3. 投放日期的选择用的是模拟点击的笨办法，可以使用[React locator](https://playwright.dev/python/docs/other-locators#react-locator)，但我试了好几次都没成功，导致在特定日期下会出现无法点击的情况
4. 上传素材时，如果素材出现网络错误（一般是重复上传视频素材导致的）可以删除此文件，但是没做，现在的做法是出现错误则取消上传
5. 选择素材时，如果选到了违规的素材则清空重新选择，更好的办法是记录下哪些是违规的素材，在选择素材的时候跳过
